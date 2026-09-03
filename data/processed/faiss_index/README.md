# FAISS Knowledge Index

This directory contains the processed FAISS vector index used by the local knowledge retrieval layer.

## Files

### index.faiss

The FAISS vector index containing the generated document embeddings.

### index_metadata.json

Metadata associated with the indexed knowledge chunks, including the extracted text and source information.

## Embedding Model

The index is generated using:

BAAI/bge-small-en-v1.5

Embeddings are normalized before indexing and the FAISS index uses L2 distance.

## Knowledge Sources

The index is generated from the project's processed institutional knowledge documents located under:

data/raw/pdf/

data/raw/docx/

## Regeneration

To rebuild the local knowledge index after modifying or adding source documents, run:

python ingest.py

The generated index files are written to this directory.
