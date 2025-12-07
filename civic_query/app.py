"""This defines a single chat endpoint and the entry point of the service.
"""
import argparse
import logging
import os
import asyncio 
from typing import List, Tuple

import uvicorn
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag_agent import RagAgent
from .utils import build_llm

llm_type = os.getenv("LLM_TYPE", "llama3")
embedding_llm_type = os.getenv("EMBEDDING_LLM_TYPE", "all-MiniLM-L6-v2")
llm = build_llm(llm_type)

agent_obj = RagAgent(llm_type, embedding_llm_type)
rag_qa_chain = agent_obj.build_rag_agent(llm)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8001",
        "http://localhost:8010",
        "http://127.0.0.1",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8010",
        "null",   # <--- CRITICAL: Allows opening index.html from your folder
        "*"       # <--- Fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("civic-query-service")

class Input(BaseModel):
    chat_input: str
    chat_history: List[Tuple[str, str]]

# 1. Define lists of keywords to catch (Simple keyword matching)
GREETING_KEYWORDS = ["hello", "hi ", "hey", "good morning", "good afternoon"]
CLOSING_KEYWORDS = ["bye", "goodbye", "thank you", "thanks", "see you", "exit", "quit"]

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    
    try:
        while True:
            data = await websocket.receive_json()
            current_input = data.get("chat_input", "").strip()

            if not current_input:
                continue

            logger.info(f"Received query: {current_input}")
            
            # Convert to lowercase for matching
            user_text_lower = current_input.lower()

            # --- ROUTER LOGIC ---

            # A. CHECK FOR CLOSINGS / GRATITUDE ("Thank you bye", "Thanks", "Goodbye")
            # We check if any of the closing keywords exist in the user string
            if any(word in user_text_lower for word in CLOSING_KEYWORDS):
                # Static response for closings
                closing_response = "You're welcome! If you have more questions about the G7 Challenge, feel free to ask. Good luck!"
                
                # Stream it
                tokens = closing_response.split(" ")
                for t in tokens:
                    await websocket.send_json({"token": t + " "})
                    await asyncio.sleep(0.05)
                
                # IMPORTANT: Send EMPTY sources to prevent the box from showing
                await websocket.send_json({
                    "end_of_stream": True,
                    "sources": [] 
                })
                continue # Skip the RAG chain

            # B. CHECK FOR GREETINGS ("Hello", "Hi")
            elif any(word in user_text_lower for word in GREETING_KEYWORDS):
                greeting_response = "Hello! I am CivicQuery. I can help you navigate the G7 GovAI Challenge guidelines. What would you like to know?"
                
                for t in greeting_response.split(" "):
                    await websocket.send_json({"token": t + " "})
                    await asyncio.sleep(0.05)
                
                await websocket.send_json({
                    "end_of_stream": True,
                    "sources": [] 
                })
                continue

            # --- C. THE RAG CHAIN (Only runs for actual questions) ---
            response_payload = await rag_qa_chain.ainvoke({"query": current_input})
            
            answer_text = response_payload["result"]
            source_docs = response_payload.get("source_documents", [])

            # Stream Answer
            tokens = answer_text.split(" ") 
            for t in tokens:
                await websocket.send_json({"token": t + " "})
                await asyncio.sleep(0.05) 

            # Process Sources
            clean_sources = []
            seen_sources = set()
            
            for doc in source_docs:
                source_path = doc.metadata.get("source", "Document")
                source_name = os.path.basename(source_path)
                page_num = doc.metadata.get("page", 0)
                
                unique_key = f"{source_name}-{page_num}"
                if unique_key not in seen_sources:
                    clean_sources.append({
                        "name": source_name,
                        "page": page_num + 1
                    })
                    seen_sources.add(unique_key)

            # Send Sources
            await websocket.send_json({
                "end_of_stream": True,
                "sources": clean_sources 
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close(code=1011)
        
@app.get("/status")
def status():
    return Response(content="App is up and running!")

def start() -> None:
    parser = argparse.ArgumentParser(description="Civic Query Service")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    uvicorn.run("civic_query.app:app", host=args.host, port=args.port, log_level="info")
