
## Flexible Multi-Agent Knowledge Management Platform
## Practical Use Case: Academic Guidance Portal for Syrian Virtual University (SVU)

Agent Knowledge Management Platform** designed to provide evidence-based academic guidance by combining local document retrieval, controlled official web retrieval, multilingual query processing, and flexible Large Language Model (LLM) providers.


## Overview

The platform follows a modular architecture consisting of three specialized agents:

* **Knowledge Retrieval Agent** — retrieves relevant evidence from the local FAISS-based knowledge base and coordinates controlled web retrieval when required.
* **Knowledge Sufficiency Agent** — evaluates whether the retrieved evidence is sufficient to support a response.
* **Response Generation Agent** — generates the final evidence-grounded response using the available context or abstains when valid evidence is unavailable.

The system also provides a provider abstraction layer that supports a local LLM as the primary provider and a cloud LLM as a fallback provider.

## Project Objective

The main objective is to develop a flexible knowledge management platform capable of:

* Retrieving knowledge from institutional documents.
* Supporting PDF and Word knowledge sources.
* Applying Retrieval-Augmented Generation (RAG).
* Supporting Arabic and English user queries.
* Using controlled official web retrieval when local evidence is insufficient or when a supported web intent is detected.
* Evaluating evidence sufficiency before response generation.
* Preventing unsupported responses through abstention.
* Providing source attribution for generated answers.
* Supporting multiple LLM providers through a unified provider interface.
* Maintaining a clear separation between the user interface, retrieval, evidence evaluation, generation, and LLM provider components.


## Project Structure

The project is organized into separate modules according to their responsibilities:

```text
Flexible-Multi-Agent-Knowledge-Platform/
├── app.py
├── pipeline_core.py
├── ingest.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── data/
│   ├── raw/
│   │   ├── pdf/
│   │   │   └── academic_guide_en.pdf
│   │   └── docx/
│   │       └── student_services_en.docx
│   │
│   └── processed/
│       └── faiss_index/
│           ├── index.faiss
│           └── index_metadata.json
│
└── src/
    ├── __init__.py
    │
    ├── agents/
    │   ├── __init__.py
    │   ├── retrieval_agent.py
    │   ├── sufficiency_agent.py
    │   └── generation_agent.py
    │
    ├── tools/
    │   ├── __init__.py
    │   ├── rag_tool.py
    │   └── web_retriever.py
    │
    └── llm/
        ├── __init__.py
        ├── local_llm.py
        ├── groq_llm.py
        └── llm_provider.py
```

`index.faiss` and `index_metadata.json` are generated processing artifacts and are excluded from Git through `.gitignore`.

## Key Features

### Multi-Agent Architecture

The system contains three operational agents:

#### 1. Knowledge Retrieval Agent

Responsible for:

* Retrieving relevant information from the local FAISS knowledge base.
* Applying the configured similarity threshold.
* Coordinating controlled official web retrieval.
* Returning the evidence required by subsequent pipeline stages.

#### 2. Knowledge Sufficiency Agent

Responsible for:

* Evaluating whether retrieved evidence is sufficient.
* Checking the availability of acceptable local or web evidence.
* Preventing response generation when sufficient evidence is unavailable.
* Supporting the system's abstention behavior.

#### 3. Response Generation Agent

Responsible for:

* Constructing the final context from retrieved evidence.
* Generating an evidence-grounded answer.
* Maintaining the user's original language.
* Providing source attribution.
* Applying an internal context guard before calling the LLM.
* Abstaining when the generation context is empty or invalid.

## System Architecture

The operational pipeline is:

```text
User Query
    │
    ▼
Language Router
    │
    ├── Arabic ──► English Retrieval Query
    │
    └── English
    │
    ▼
Web Intent Detection
    │
    ├── Known Intent ──► Controlled Official SVU Web Retrieval
    │
    └── No Known Intent
              │
              ▼
     Knowledge Retrieval Agent
              │
              ▼
        Local FAISS Retrieval
              │
              ▼
     Knowledge Sufficiency Agent
              │
        ┌─────┴─────┐
        │           │
   Sufficient   Insufficient
        │           │
        │           ▼
        │      Web Fallback
        │           │
        │           ▼
        └──────► Retrieved Evidence
                       │
                       ▼
            Response Generation Agent
                       │
                       ▼
                  LLMProvider
                       │
              ┌────────┴────────┐
              │                 │
        Primary Provider   Fallback Provider
              │                 │
              ▼                 ▼
          LM Studio          Groq API
              │                 │
              ▼                 ▼
      Qwen2.5-3B-Instruct   GPT-OSS 20B
              │                 │
              └────────┬────────┘
                       │
                       ▼
                  Final Output
                       │
              ┌────────┴────────┐
              │                 │
     Final Answer + Sources   Abstention
```

## Retrieval-Augmented Generation

The local knowledge pipeline implements Retrieval-Augmented Generation (RAG) through the following stages:

1. **Source Documents**
   PDF and Word documents are used as the institutional knowledge sources.

2. **Text Extraction**
   Text is extracted from PDF and Word documents.

3. **Text Cleaning**
   Extracted content is normalized and cleaned.

4. **Chunking**
   Documents are divided into smaller overlapping text chunks.

5. **Embedding Generation**
   Text chunks are converted into vector representations using `BAAI/bge-small-en-v1.5`.

6. **FAISS Indexing**
   The embeddings are stored in a local FAISS `IndexFlatL2` vector index.

7. **Similarity Retrieval**
   The system retrieves the most relevant chunks for the user's query.

8. **Evidence-Based Generation**
   Retrieved evidence is passed to the generation stage and used as the context for the LLM.

The Retrieval Agent requests up to five local results and accepts local evidence according to the configured L2 similarity threshold, where lower L2 distance represents greater similarity.

## Evidence Sufficiency & Abstention

The platform uses evidence-based response control at two stages:

1. **Knowledge Sufficiency Agent**
   Evaluates whether acceptable local or web evidence is available before response generation. If sufficient evidence is not available, the system returns an abstention response rather than generating an unsupported answer.

2. **Response Generation Agent**
   Applies an internal context guard before calling the LLM. If the supplied context is empty or invalid, the agent abstains instead of generating a response.

This layered approach helps keep generated responses grounded in retrieved evidence and reduces the risk of unsupported answers.

## Multilingual Processing

The system supports both **Arabic and English queries**.

For Arabic queries:

1. The Language Router identifies the query as Arabic.
2. The query is translated into English for local retrieval because the current institutional knowledge documents are in English.
3. Retrieval is performed using the English retrieval query.
4. The original Arabic query is preserved.
5. The final response is generated in the user's original language.

English queries proceed directly to retrieval without the translation step.

## Controlled Web Retrieval

The system does not perform unrestricted web browsing.

Instead, it uses a controlled web retrieval mechanism based on predefined official SVU sources and supported web intents.

Current supported intents include:

* Student affairs.
* Thesis defenses.
* University news.

The web retriever:

* Uses predefined official SVU pages.
* Detects supported Arabic and English intent keywords.
* Retrieves and cleans page content.
* Removes unnecessary HTML elements such as scripts and styles.
* Limits the amount of retrieved web content.
* Uses web retrieval as a controlled fallback when acceptable local evidence is unavailable.

This approach is intended to maintain a controlled and institution-focused external knowledge source.

## LLM Provider Architecture

The platform uses an `LLMProvider` abstraction to separate the application pipeline from individual LLM implementations.

### Primary Provider

**LM Studio — Qwen2.5-3B-Instruct**

* Runs locally through the LM Studio OpenAI-compatible API.
* Used as the primary generation provider.
* Suitable for local development and offline-capable model execution when the local model server is available.

### Fallback Provider

**Groq API — GPT-OSS 20B**

* Used when the primary local provider fails.
* Requires a valid `GROQ_API_KEY`.
* Provides a cloud-based fallback generation path.

The provider architecture allows the rest of the application to use a unified interface without depending directly on a specific LLM implementation.

## Web Interface

The application provides a Streamlit-based web interface for the Academic Guidance Portal.

The interface supports:

* Arabic and English queries.
* Final answer display.
* Source attribution.
* Pipeline status information.
* Generation provider information.
* Explicit abstention status.
* Recent query history.
* Restoring recent questions without rerunning the pipeline.

The user interface is separated from the core pipeline logic, allowing the retrieval and generation components to operate independently from the presentation layer.

## Technology Stack

| Category                  | Technologies                   |
| ------------------------- | ------------------------------ |
| Programming Language      | Python                         |
| User Interface            | Streamlit                      |
| Architecture              | Multi-Agent Architecture       |
| Retrieval                 | FAISS, LangChain               |
| Embeddings                | BAAI/bge-small-en-v1.5         |
| PDF Processing            | PyPDF                          |
| Word Processing           | python-docx                    |
| Web Retrieval             | Requests, BeautifulSoup        |
| Local LLM                 | LM Studio, Qwen2.5-3B-Instruct |
| Cloud LLM                 | Groq API, GPT-OSS 20B          |
| Environment Configuration | python-dotenv                  |
| Vector Search             | FAISS IndexFlatL2              |

## Installation & Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform
cd Flexible-Multi-Agent-Knowledge-Platform
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv flexible_multi_agent_env
.\flexible_multi_agent_env\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` to the repository. It is excluded through `.gitignore`.

### 5. Configure the Local LLM

For the primary generation path:

* Install and run LM Studio.
* Load `Qwen2.5-3B-Instruct`.
* Start the local OpenAI-compatible server.
* Ensure the configured local endpoint is available to the application.

The default local endpoint is:

```text
http://127.0.0.1:1234/v1/chat/completions
```

## Running the Application

### Build or Rebuild the Local Knowledge Index

Run:

```powershell
python ingest.py
```

The ingestion process extracts and processes the configured PDF and Word sources and creates the local FAISS index and metadata.

### Start the Streamlit Application

Run:

```powershell
streamlit run app.py
```

The application then provides the Academic Guidance Portal interface through Streamlit.

## Knowledge Ingestion

The current knowledge base contains:

* `academic_guide_en.pdf`
* `student_services_en.docx`

The ingestion pipeline performs:

* PDF text extraction.
* Word document text extraction.
* Text normalization.
* Chunk creation.
* Embedding generation.
* FAISS vector index creation.
* Metadata generation.

The generated local artifacts are:

```text
data/processed/faiss_index/
├── index.faiss
└── index_metadata.json
```

These generated files are excluded from version control.

## Retrieval Configuration

The current retrieval implementation uses:

* Embedding model: `BAAI/bge-small-en-v1.5`
* Vector index: FAISS `IndexFlatL2`
* Retrieval request: up to 5 chunks
* Local similarity threshold: `0.65` L2 distance
* Lower L2 distance: better similarity

The retrieval stage returns evidence and metadata that are subsequently evaluated by the Knowledge Sufficiency Agent.

## Scope & Limitations

### Current Scope

The current implementation focuses on:

* Academic guidance.
* Syrian Virtual University institutional information.
* PDF and Word knowledge sources.
* Controlled official SVU web retrieval.
* Arabic and English queries.
* Retrieval-Augmented Generation.
* Evidence sufficiency evaluation.
* Abstention behavior.
* Local and cloud LLM providers.
* Streamlit-based web interaction.

### Current Limitations

The current project does not include:

* Unrestricted web search.
* Image processing.
* Advanced OCR.
* LLM training or fine-tuning.
* Embedding model training or fine-tuning.
* Authentication and authorization.
* Smartphone applications.
* Microservices architecture.
* A production-scale distributed vector database.
* Per-subquestion semantic sufficiency evaluation.

The current local FAISS index is generated during the knowledge ingestion process and is not committed to the Git repository.

## Future Development

Possible future extensions include:

* Adding more institutional knowledge sources.
* Expanding controlled official web coverage.
* Improving multilingual retrieval.
* Adding additional LLM providers.
* Introducing retrieval reranking.
* Expanding evaluation and benchmarking capabilities.
* Supporting image and OCR-based knowledge sources.
* Adding authentication and authorization.
* Deploying the platform to a cloud environment.
* Scaling the architecture for larger institutional knowledge bases.

These items represent potential future development and are not part of the current implementation.

## Academic Project

**Project:** Flexible Multi-Agent Knowledge Management Platform

**Application:** Academic Guidance Portal for the Syrian Virtual University

**Project Type:** Graduation Project

**Primary Focus:**

* Multi-Agent Systems
* Retrieval-Augmented Generation (RAG)
* Evidence-Based Response Generation
* Knowledge Sufficiency Evaluation
* Controlled Web Retrieval
* Multilingual Query Processing
* LLM Provider Abstraction

## License

This project is currently provided as an academic graduation project.

A formal open-source license may be added in a future release.
