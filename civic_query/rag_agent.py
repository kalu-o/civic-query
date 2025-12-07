"""The RagAgent class that handles creation of embeddings and retrieval.
"""
import os
from dataclasses import dataclass
from typing import List

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

chunk_size = int(os.getenv("CHUNK_SIZE", "1500"))
chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
# Set this to True to get citations
return_source_documents = True 

@dataclass
class RagAgent:
    llm_type: str
    embedding_llm_type: str

    def load_documents(self, document_directory: str) -> List[Document]:
        loader = PyPDFDirectoryLoader(document_directory, silent_errors=True)
        documents = loader.load()
        return documents

    def split_documents(self, document_directory: str) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        documents = self.load_documents(document_directory)
        return text_splitter.split_documents(documents)

    def store_embedding(self, split_document: List[Document], persist_directory: str) -> None:
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_llm_type)
        vector_db = Chroma.from_documents(
            documents=split_document,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        vector_db.persist()

    def create_embedding(self, document_directory: str, persist_directory: str) -> None:
        split_document = self.split_documents(document_directory)
        self.store_embedding(split_document, persist_directory)

    def load_embedding(self, persist_directory: str) -> Chroma:
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_llm_type)
        vector_db = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )
        return vector_db

    def build_rag_agent(self, llm: ChatOpenAI, persist_directory: str = "/tmp"):
        vector_db = self.load_embedding(persist_directory)

        # --- UPDATED PROMPT FOR G7 ---
        # We explicitly tell it to handle greetings naturally.
        template = """You are 'CivicQuery', an AI assistant for the G7 GovAI Challenge.
        
        INSTRUCTIONS:
        1. If the user input is a GREETING (e.g., "Hello", "Hi") or COMPLIMENT, respond politely and briefly WITHOUT using the context.
        2. For specific questions, base your answer ONLY on the provided Context.
        3. If the answer is not in the context, say: "I cannot find this information in the official documents."
        
        Context:
        {context}
        
        Question: {question}
        
        Helpful Answer:"""
        
        qa_chain_prompt = PromptTemplate.from_template(template)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vector_db.as_retriever(search_type="mmr"),
            return_source_documents=True, 
            chain_type_kwargs={"prompt": qa_chain_prompt},
        )
        return qa_chain
        
            
        qa_chain_prompt = PromptTemplate.from_template(template)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vector_db.as_retriever(search_type="mmr"),
            return_source_documents=True, # Explicitly set to True
            chain_type_kwargs={"prompt": qa_chain_prompt},
        )
        return qa_chain
