
## Flexible Multi-Agent Knowledge Management Platform

## Practical Use Case: Academic Guidance Portal for Syrian Virtual University (SVU)

A modular **Retrieval-Augmented Generation (RAG)** platform that combines local institutional knowledge, controlled web retrieval, multi-agent processing, evidence-based generation, source attribution, and controlled abstention.

The platform is designed as a flexible knowledge management architecture that can be adapted to institutional domains where answers should be generated from trusted knowledge sources rather than from unrestricted model knowledge.

---

## Overview

The **Flexible Multi-Agent Knowledge Management Platform** provides an academic guidance use case for the **Syrian Virtual University (SVU)**.

The system processes user queries through a structured pipeline that combines:

1- Local document retrieval from a FAISS vector index.

2- Knowledge Sufficiency Agent for evaluating whether the retrieved evidence is sufficient.

3- Controlled retrieval from predefined official SVU web pages when required.

4- Arabic and English query routing.

5- Evidence-based response generation.

6- Source attribution.

7- Evidence-constrained abstention when sufficient supporting information is unavailable.

8- Local-to-cloud Large Language Model (LLM) provider fallback.

The current implementation focuses on demonstrating a reliable and explainable knowledge retrieval workflow rather than unrestricted general-purpose question answering.

---

---

## Project Purpose

This project demonstrates how a modular multi-agent architecture can combine knowledge retrieval, evidence evaluation, controlled access to external knowledge, and language-model generation to build a more reliable knowledge-oriented platform.

The architecture is intentionally separated into independent components so that the knowledge sources, retrieval mechanisms, agents, and LLM providers can be extended or replaced without redesigning the entire application.

---

## System Architecture

The platform follows a multi-stage processing pipeline:

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
    └── No Known Intent ──► Local FAISS Retrieval
    │
    ▼
Knowledge Sufficiency agent
    │
    ├── Sufficient ───────────────┐
    │                             │
    └── Insufficient ──► Web Fallback
                                  │
                                  ▼
                    Response Generation Agent
                                  │
                                  ▼
                           LLM Provider
                    ┌──────────────┴──────────────┐
                    │                             │
             Local Primary                 Cloud Fallback
          Qwen2.5-3B-Instruct            GPT-OSS 20B
             via LM Studio                  via Groq
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                              Final Output
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                Final Answer + Sources   Abstention
```

---

## Multi-Agent Architecture

The system uses three specialized agents:

### 1. Retrieval Agent

Responsible for retrieving relevant knowledge from the local FAISS-based knowledge base and coordinating retrieval-related operations.

### 2. Knowledge Sufficiency Agent

Evaluates whether the retrieved evidence provides sufficient information to answer the user's request.

When the available evidence is insufficient, the system can activate the controlled web fallback for supported intents.

### 3. Response Generation Agent

Generates the final response using the available evidence while applying source attribution and evidence-constrained response behavior, or explicitly abstains when sufficient evidence is unavailable.

The system is designed to avoid unsupported answers by grounding responses in available evidence and explicitly abstaining when sufficient evidence is unavailable.

---

## Retrieval-Augmented Generation

The local knowledge base is implemented using **FAISS (Facebook AI Similarity Search)**.

The ingestion pipeline processes institutional documents through:

```text
Source Documents
      │
      ▼
Text Extraction
      │
      ▼
Cleaning
      │
      ▼
Chunking
      │
      ▼
Embeddings
      │
      ▼
FAISS Vector Index
      │
      ▼
Similarity Retrieval
      │
      ▼
Retrieved Evidence
```

The current knowledge base contains English-translated institutional documents used for the academic guidance use case.

The embedding model currently used by the project is:

```text
BAAI/bge-small-en-v1.5
```

The vector index uses normalized embeddings with FAISS `IndexFlatL2`.

---

## Multilingual Query Processing

The system supports Arabic and English user queries.

Because the current embedding model is English-oriented, Arabic queries are routed through a language processing layer that converts the retrieval query into English before semantic retrieval.

The general flow is:

```text
Arabic Query
     │
     ▼
Language Detection
     │
     ▼
English Retrieval Query
     │
     ▼
FAISS Retrieval
     │
     ▼
Evidence-Based Generation
     │
     ▼
Arabic / English Response
```

This approach allows the current English knowledge representation and embedding model to be used while maintaining Arabic query support.

---

## Controlled Web Retrieval

The platform does not perform unrestricted web search.

Web retrieval is restricted to predefined official Syrian Virtual University pages associated with supported intents.

The current controlled web sources include:

```text
University News
https://www.svuonline.org/ar/node/506

Student Affairs
https://www.svuonline.org/ar/node/231

Thesis Defenses
https://www.svuonline.org/ar/node/3641
```

The web retrieval layer includes bilingual intent normalization to improve recognition of supported Arabic and English query forms.

If a query does not match a supported web intent, the system continues through the local knowledge retrieval path.

---

## Evidence Sufficiency and Abstention

A central design principle of the platform is that the language model should operate within the boundaries of the available evidence.

When sufficient evidence exists, the system generates an evidence-based response.

When sufficient evidence is unavailable, the system can abstain from providing unsupported factual information.

For example, a query containing both a supported academic requirement and an unrelated unsupported financial fact can produce a response that addresses the supported academic component while explicitly indicating that adequate evidence is unavailable for the unsupported component.

This behavior is intended to reduce unsupported generation and improve response reliability.

---

## Source Attribution

The platform provides dynamic source attribution for retrieved evidence.

Sources are associated with the actual retrieval process rather than being static interface metadata.

Depending on the query, the final response may reference one or multiple knowledge sources, such as:

```text
academic_guide_en.pdf
student_services_en.docx
```

This provides traceability between the generated response and the knowledge used to produce it.

---

## LLM Provider Architecture

The system supports a local primary model and a cloud fallback provider.

### Local Primary

```text
LM Studio
Qwen2.5-3B-Instruct
```

The local provider allows the system to operate without requiring a cloud LLM for normal execution.

### Cloud Fallback

```text
Groq API
GPT-OSS 20B
```

If the local provider is unavailable or fails during execution, the provider layer can switch to the configured Groq fallback.

This design separates the application pipeline from the specific LLM provider and makes the generation layer more flexible.

---

## Operational Interface

The project includes a Streamlit-based interface for interacting with the platform.

The interface presents:

```text
Final Answer

Pipeline Status
    Local Retrieval
    Web Fallback
    Generation Provider

Source Attribution

Recent Questions
```

The displayed pipeline information represents the execution state of the current query.

This provides a lightweight **operational observability layer** that makes the system behavior easier to inspect during testing and demonstration.

---

## Project Structure

```text
Flexible-Multi-Agent-Knowledge-Platform/
│
├── app.py
├── pipeline_core.py
├── ingest.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── data/
│   ├── processed/
│   │   └── faiss_index/
│   │       ├── README.md
│   │       ├── index.faiss
│   │       └── index_metadata.json
│   │
│   └── raw/
│       ├── pdf/
│       │   └── academic_guide_en.pdf
│       │
│       └── docx/
│           └── student_services_en.docx
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

---

## Main Components

| Component |                           Responsibility                           |
| ----------------------- | ---------------------------------------------------- |
| `app.py`                | Streamlit user interface and application entry point |
| `pipeline_core.py`      | Core pipeline coordination                           |
| `ingest.py`             | Knowledge ingestion and FAISS index construction     |
| `retrieval_agent.py`    | Knowledge retrieval operations                       |
| `sufficiency_agent.py`  | Evidence sufficiency assessment                      |
| `generation_agent.py`   | Evidence-based response generation                   |
| `rag_tool.py`           | Local FAISS retrieval tool                           |
| `web_retriever.py`      | Controlled official SVU web retrieval                |
| `local_llm.py`          | Local LLM integration                                |
| `groq_llm.py`           | Groq API integration                                 |
| `llm_provider.py`       | LLM provider selection and fallback                  |

---

## Knowledge Base

The current demonstration knowledge base contains institutional SVU material represented in English for compatibility with the current embedding model.

Current source documents include:

```text
academic_guide_en.pdf
student_services_en.docx
```

The generated FAISS knowledge index is stored under:

```text
data/processed/faiss_index/
```

The repository includes the index metadata required by the retrieval layer.

---

## Configuration

The project uses environment variables for provider configuration.

Create a `.env` file in the project root and configure the required API credentials for the cloud fallback provider.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

Do not commit real API keys or other secrets to GitHub.

The `.gitignore` file should be used to prevent sensitive configuration files and local environment artifacts from being committed.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform.git
cd Flexible-Multi-Agent-Knowledge-Platform
```

Create and activate a Python virtual environment:

```bash
python -m venv flexible_multi_agent_env
```

Windows PowerShell:

```powershell
.\flexible_multi_agent_env\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

After startup, open the local Streamlit address displayed in the terminal.

The application then provides the academic guidance interface and the operational pipeline status for each query.

---

## Knowledge Ingestion

If the source documents are modified or new documents are introduced, the FAISS knowledge index can be regenerated using the ingestion script:

```bash
python ingest.py
```

The ingestion process creates the processed vector index and associated metadata used by the retrieval layer.

---

## Evaluation

The implemented system has been evaluated across several functional areas, including:

```text
Core Architecture
Retrieval
Translation
LLM Provider
Controlled Web Retrieval
Source Attribution
Abstention
Grounded Generation
```

The evaluation also included mixed-sufficiency and composite-query scenarios to examine how the system handles requests containing both supported and unsupported information requirements.

The results demonstrated that the system can retrieve evidence from multiple sources, identify insufficient evidence, use controlled web retrieval for supported intents, attribute retrieved sources, and constrain responses when evidence is unavailable.

---

## Design Principles

The project follows several core engineering principles:

1- **Modularity**
Core responsibilities are separated into agents, tools, retrieval components, and LLM provider modules.

2- **Evidence-Based Generation**
Responses are generated using retrieved evidence rather than relying solely on the language model's internal knowledge.

3- **Controlled Retrieval**
Web retrieval is limited to predefined trusted SVU sources.

4- **Provider Flexibility**
The generation layer can operate with a local LLM and a configured cloud fallback.

5- **Source Traceability**
Retrieved knowledge sources are exposed as part of the final system output.

6- **Abstention**
The system avoids presenting unsupported information as factual when adequate evidence is unavailable.

7- **Separation of Concerns**
Retrieval, sufficiency assessment, generation, web access, and provider management are implemented as separate components.

---

## Current Scope and Limitations

The current implementation is a focused academic guidance use case rather than a production-scale institutional deployment.

The local knowledge base currently contains a limited set of SVU documents.

The embedding model is English-oriented, so Arabic retrieval relies on the language routing and translation layer.

Controlled web retrieval is currently limited to predefined official SVU pages and supported intents.

The system is designed to demonstrate the architecture and its reliability mechanisms within the defined project scope.

---

## Future Development

Potential future extensions include:

1- Expansion of the institutional knowledge base.

2- Support for additional trusted information sources.

3- More advanced multilingual embedding models.

4- Enhanced retrieval and ranking strategies.

5- Persistent conversation and query history.

6- Performance optimization and caching for larger-scale deployments.

These items are outside the current implementation and are presented as possible future extensions rather than existing system capabilities.

---

## Technology Stack

```text
Python
Streamlit
CrewAI
FAISS
Sentence Transformers
BAAI/bge-small-en-v1.5
PyPDF
python-docx
LM Studio
Qwen2.5-3B-Instruct
Groq API
GPT-OSS 20B
```



## Author

Developed as an Artificial Intelligence Diploma graduation project.

**Project:** Flexible Multi-Agent Knowledge Management Platform
**Use Case:** Academic Guidance Portal for Syrian Virtual University (SVU)

---

## License

This project is provided for educational and research purposes.

If a specific open-source license is selected for the repository, this section should be updated accordingly.
