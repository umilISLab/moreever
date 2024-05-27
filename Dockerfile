FROM python:3-slim-buster

ARG ISO_LANGUAGE
ENV ISO_LANG $ISO_LANGUAGE

EXPOSE 8000

COPY requirements.txt /

# ADD corpora.tar.xz /app
# ADD vocab.tar.xz /app

RUN apt-get update && apt-get install wget -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    python -m nltk.downloader punkt wordnet && \
    python -m spacy download ${ISO_LANGUAGE}_core_web_lg
    
WORKDIR /app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
