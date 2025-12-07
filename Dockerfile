ARG DOCKER_REGISTRY=docker.io
FROM ${DOCKER_REGISTRY}/library/python:3.10-slim-bookworm


RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get -qq update \
    && apt-get -qq upgrade \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt dist/civic_query_service-*.whl /app/
COPY data/chroma/ /tmp/

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps --find-links . civic_query_service

EXPOSE 8001/tcp

ENTRYPOINT ["civic_query_service"]
