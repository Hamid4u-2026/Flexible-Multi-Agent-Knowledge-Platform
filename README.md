
##  Flexible Multi-Agent Knowledge Management Platform
## Use Case: Academic Guidance Portal for Syrian Virtual University (SVU)


> **An Intelligent Retrieval-Augmented Generation (RAG) system combining local institutional knowledge, controlled web retrieval, multi-agent processing, and evidence-based generation.**

A modular knowledge management architecture designed for institutional domains where answers should be generated from trusted knowledge sources rather than from unrestricted model knowledge.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [Evaluation Results](#evaluation-results)
- [Design Principles](#design-principles)
- [Scope & Limitations](#scope--limitations)
- [Future Development](#future-development)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

---

## 🎯 Overview

This platform is developed as an **AI Diploma graduation project** demonstrating how a modular multi-agent architecture can combine knowledge retrieval, evidence evaluation, controlled external access, and language model generation to build a more reliable and explainable knowledge-oriented system.

**Use Case:** Academic Guidance Portal for Syrian Virtual University (SVU)

The system processes user queries through a structured pipeline that combines:

1. **Local document retrieval** from a FAISS vector index
2. **Knowledge Sufficiency Agent** for evaluating retrieved evidence
3. **Controlled retrieval** from predefined official SVU web pages
4. **Multilingual query routing** (Arabic ↔ English)
5. **Evidence-based response generation**
6. **Source attribution** for all answers
7. **Evidence-constrained abstention** when information is insufficient
8. **Local-to-cloud LLM provider fallback** mechanism

---

## 🚀 Key Features

### ✅ Intelligent Query Processing
- Automatic Arabic to English query conversion for retrieval
- Web intent detection for controlled external access
- Multilingual support (Arabic & English)
- Mixed-query handling (supported & unsupported components)

### ✅ Evidence-Based RAG Pipeline
```
Source Documents
    ↓
Text Extraction & Cleaning
    ↓
Semantic Chunking
    ↓
Embedding Generation (BAAI/bge-small-en-v1.5)
    ↓
FAISS Vector Index (IndexFlatL2, Normalized)
    ↓
Semantic Similarity Retrieval
    ↓
Evidence-Based Response
```

### ✅ Knowledge Sufficiency Assessment
- Automatic evaluation of retrieved evidence adequacy
- Conditional web fallback activation
- Ensures evidence-grounded responses

### ✅ Controlled Web Retrieval
Only predefined official SVU sources:
- 📰 **University News** - https://www.svuonline.org/ar/node/506
- 👥 **Student Affairs** - https://www.svuonline.org/ar/node/231
- 🎓 **Thesis Defenses** - https://www.svuonline.org/ar/node/3641

### ✅ Dynamic Source Attribution
Sources are retrieved during execution and attributed to generated responses:
- `academic_guide_en.pdf`
- `student_services_en.docx`

### ✅ Evidence-Constrained Responses
- Generate answers only when sufficient evidence exists
- Explicitly abstain from unsupported information
- Reduce hallucinations and improve reliability

### ✅ Flexible LLM Provider Architecture
| Provider Type | Implementation | Model |
|---|---|---|
| **Local Primary** | LM Studio | Qwen2.5-3B-Instruct |
| **Cloud Fallback** | Groq API | GPT-OSS 20B |

---

## 🏗️ System Architecture

### Processing Pipeline

```
User Query
    ↓
Language Router
    ├── Arabic ──→ English Retrieval Query
    └── English
    ↓
Web Intent Detection
    ├── Known Intent ──→ Controlled Official SVU Web Retrieval
    └── No Known Intent ──→ Local FAISS Retrieval
    ↓
Knowledge Sufficiency Assessment
    ├── Sufficient ──────────────┐
    └── Insufficient ──→ Web Fallback
                                ↓
                    Response Generation Agent
                                ↓
                            LLM Provider
                    ┌─────────────┴─────────────┐
                    ↓                           ↓
            Local (Qwen2.5-3B)        Cloud (Groq/GPT-OSS)
                    └─────────────┬─────────────┘
                                ↓
                            Final Output
                    ┌─────────────┴─────────────┐
                    ↓                           ↓
            Final Answer + Sources          Abstention
```

### Multi-Agent Architecture

The system uses three specialized agents:

#### 1. **Retrieval Agent**
- Responsible for retrieving relevant knowledge from the local FAISS-based knowledge base
- Coordinates retrieval-related operations
- Manages semantic similarity searches

#### 2. **Knowledge Sufficiency Agent**
- Evaluates whether retrieved evidence is sufficient to answer the query
- Determines when to activate controlled web fallback
- Assesses evidence quality and relevance

#### 3. **Response Generation Agent**
- Generates final responses using available evidence
- Applies source attribution dynamically
- Implements evidence-constrained behavior
- Explicitly abstains when sufficient evidence is unavailable

---

## 📦 Installation & Setup

### Prerequisites

- **Python** 3.8 or higher
- **Git** for version control
- **pip** package manager
- **Virtual Environment** (recommended)

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform.git
cd Flexible-Multi-Agent-Knowledge-Platform
```

#### 2. Create Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv flexible_multi_agent_env
.\flexible_multi_agent_env\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv flexible_multi_agent_env
source flexible_multi_agent_env/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Create .env file in project root
touch .env

# Add the following (update with your actual API key):
GROQ_API_KEY=your_api_key_here
```

⚠️ **Security Warning:** Never commit actual API keys to GitHub. Use `.gitignore` to prevent sensitive files from being tracked.

#### 5. Verify Installation
```bash
python -c "import faiss; import streamlit; print('Installation successful!')"
```

---

## 🎮 Usage Guide

### Running the Application

```bash
streamlit run app.py
```

The application will start and display a local URL (typically `http://localhost:8501`). Open this URL in your browser.

### User Interface Components

The Streamlit interface provides:

1. **Query Input Field**
   - Enter questions in Arabic or English
   - Natural language processing handles both languages

2. **Final Answer Display**
   - Evidence-based response
   - Clear, concise answers grounded in retrieved documents

3. **Pipeline Status Dashboard**
   - Local Retrieval Status
   - Web Fallback Status
   - Generation Provider Used
   - Real-time execution transparency

4. **Source Attribution Section**
   - Dynamic source references
   - Document names and relevance indicators
   - Complete traceability

5. **Question History**
   - Previous queries and responses
   - Quick access to past interactions

### Regenerating the Knowledge Index

When source documents are modified or new documents are added:

```bash
python ingest.py
```

This script will:
- Extract text from PDF and DOCX files
- Clean and chunk the content
- Generate embeddings
- Create an updated FAISS index
- Store metadata for retrieval

---

## 📁 Project Structure

```
Flexible-Multi-Agent-Knowledge-Platform/
│
├── app.py                              # Streamlit UI & entry point
├── pipeline_core.py                    # Core pipeline orchestration
├── ingest.py                           # Knowledge ingestion & FAISS indexing
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (local only)
├── .env.example                        # Example environment configuration
├── .gitignore                          # Git ignore rules
├── README.md                           # Project documentation
├── LICENSE                             # License file
│
├── data/
│   ├── processed/
│   │   └── faiss_index/               # FAISS vector database
│   │       ├── README.md
│   │       ├── index.faiss            # Vector index file
│   │       └── index_metadata.json    # Index metadata & config
│   │
│   └── raw/
│       ├── pdf/
│       │   └── academic_guide_en.pdf  # Sample source document
│       │
│       └── docx/
│           └── student_services_en.docx  # Sample source document
│
└── src/
    ├── __init__.py
    │
    ├── agents/                         # Specialized agents
    │   ├── __init__.py
    │   ├── retrieval_agent.py         # Knowledge retrieval
    │   ├── sufficiency_agent.py       # Evidence evaluation
    │   └── generation_agent.py        # Response generation
    │
    ├── tools/                          # Helper tools
    │   ├── __init__.py
    │   ├── rag_tool.py                # FAISS retrieval tool
    │   └── web_retriever.py           # Controlled web retrieval
    │
    └── llm/                            # LLM provider management
        ├── __init__.py
        ├── local_llm.py               # Local LLM integration
        ├── groq_llm.py                # Groq API integration
        └── llm_provider.py            # Provider selection & fallback
```

### Core Components

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit UI, user interaction, query input |
| `pipeline_core.py` | Orchestrates the entire processing pipeline |
| `ingest.py` | Document ingestion, embedding generation, FAISS indexing |
| `retrieval_agent.py` | FAISS-based knowledge retrieval operations |
| `sufficiency_agent.py` | Evidence quality assessment |
| `generation_agent.py` | LLM-based response generation with source attribution |
| `rag_tool.py` | FAISS vector database interface |
| `web_retriever.py` | Controlled retrieval from official SVU web pages |
| `local_llm.py` | LM Studio local model integration |
| `groq_llm.py` | Groq API cloud provider integration |
| `llm_provider.py` | Automatic provider selection and fallback logic |

---

## 🛠️ Technology Stack

### Programming Languages & Frameworks
| Technology | Purpose |
|---|---|
| **Python 3.8+** | Core programming language |
| **Streamlit** | Interactive web-based user interface |
| **CrewAI** | Multi-agent orchestration framework |

### Vector Search & Embeddings
| Technology | Purpose |
|---|---|
| **FAISS** | Efficient semantic similarity search |
| **Sentence Transformers** | Embedding generation |
| **BAAI/bge-small-en-v1.5** | English-oriented embedding model |

### Document Processing
| Technology | Purpose |
|---|---|
| **PyPDF** | PDF text extraction |
| **python-docx** | DOCX document parsing |

### LLM Providers
| Provider | Model | Environment |
|---|---|---|
| **LM Studio** | Qwen2.5-3B-Instruct | Local (Primary) |
| **Groq API** | GPT-OSS 20B | Cloud (Fallback) |

### Development & Deployment
| Tool | Purpose |
|---|---|
| **pip** | Python package management |
| **Git** | Version control |
| **python-dotenv** | Environment variable management |

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Local LLM Configuration (Optional)
LOCAL_LLM_HOST=localhost
LOCAL_LLM_PORT=1234
LOCAL_LLM_TIMEOUT=300

# Application Configuration (Optional)
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### Customizing Models

#### Change Local LLM Model
Edit `src/llm/local_llm.py`:
```python
model_name = "Qwen2.5-3B-Instruct"  # Change to your desired model
```

#### Change Embedding Model
Edit `src/tools/rag_tool.py`:
```python
embedding_model = "BAAI/bge-small-en-v1.5"  # Change to another Sentence Transformer model
```

#### Add Web Sources
Edit `src/tools/web_retriever.py`:
```python
SUPPORTED_INTENTS = {
    "University News": "https://www.svuonline.org/ar/node/506",
    "Student Affairs": "https://www.svuonline.org/ar/node/231",
    "Thesis Defenses": "https://www.svuonline.org/ar/node/3641",
    "Your New Intent": "https://your-trusted-source.com"  # Add here
}
```

---

## 📊 Evaluation Results

The system has been comprehensively evaluated across multiple functional areas:

### ✅ Core Architecture
- Modular design with independent, reusable components
- Clear separation of concerns between agents and tools
- Flexible provider architecture for LLM swapping

### ✅ Retrieval Performance
- Multi-source evidence retrieval
- Semantic similarity-based ranking
- Accurate document matching

### ✅ Multilingual Processing
- Arabic query support via language routing
- Automatic query translation for English-based embeddings
- Bilingual response generation

### ✅ LLM Provider Fallback
- Seamless local-to-cloud failover
- Provider availability checking
- Graceful degradation

### ✅ Controlled Web Retrieval
- Restricted to predefined official sources
- Intent-based access control
- Bilingual intent normalization

### ✅ Source Attribution
- Dynamic source tracking during retrieval
- Accurate source-to-answer mapping
- Full traceability and transparency

### ✅ Evidence-Constrained Responses
- Explicit abstention on insufficient evidence
- Mixed-query handling (supported + unsupported components)
- Reduced hallucinations and false claims

### ✅ Grounded Generation
- Evidence-based answer formulation
- Avoidance of unsupported statements
- Improved reliability and trustworthiness

---

## 🏛️ Design Principles

The project follows seven core engineering principles:

### 1. Modularity
- Core responsibilities separated into agents, tools, and components
- Each module has a single, well-defined purpose
- Components are reusable and replaceable

### 2. Evidence-Based Generation
- Responses generated from retrieved evidence
- Minimal reliance on model's internal knowledge
- Grounded reasoning

### 3. Controlled Retrieval
- Web access limited to predefined trusted sources
- Intent-based access control
- No unrestricted internet searches

### 4. Provider Flexibility
- Local primary LLM for normal operation
- Cloud fallback for reliability
- Easy provider switching via configuration

### 5. Source Traceability
- Dynamic source attribution
- Retrieved sources exposed in final output
- Complete query-to-answer provenance

### 6. Abstention Mechanism
- System avoids presenting unsupported information as fact
- Explicit indicators when evidence is insufficient
- Improved user trust through transparency

### 7. Separation of Concerns
- Retrieval logic isolated from sufficiency assessment
- Generation decoupled from LLM provider selection
- Independent web access management

---

## 🚧 Scope & Limitations

### Current Implementation Status

| Aspect | Details |
|---|---|
| **Knowledge Base** | Limited SVU institutional documents (demonstration scope) |
| **Language Support** | English embeddings; Arabic queries via translation |
| **Web Sources** | Only predefined official SVU pages |
| **Model Size** | Small local model (3B parameters) for efficiency |
| **Deployment** | Development/demonstration focus, not production-scale |

### Known Limitations

- Embedding model is English-oriented (Arabic queries require translation)
- Web retrieval is restricted to pre-approved sources only
- Knowledge base limited to current institutional documents
- Local model has limited reasoning capabilities for complex queries
- No persistent conversation memory (session-based only)

### Design Trade-offs

- **Reliability over Capability:** Constrained responses prioritize accuracy
- **Interpretability over Scale:** Modular design favors explainability
- **Safety over Coverage:** Limited sources prioritize trustworthiness

---

## 🔮 Future Development

Potential enhancements and extensions:

### Phase 1: Knowledge Expansion
- [ ] Expand institutional knowledge base
- [ ] Add additional trusted document sources
- [ ] Support more institutional domains

### Phase 2: Multilingual Enhancement
- [ ] Implement advanced multilingual embedding models
- [ ] Direct Arabic language support
- [ ] Support for additional languages

### Phase 3: Advanced Retrieval
- [ ] Hybrid retrieval (semantic + keyword)
- [ ] Multi-hop reasoning
- [ ] Ranking and relevance optimization
- [ ] Query expansion techniques

### Phase 4: User Experience
- [ ] Persistent conversation history
- [ ] User feedback mechanism
- [ ] Query refinement suggestions
- [ ] Performance analytics dashboard

### Phase 5: Scale & Production
- [ ] Performance optimization and caching
- [ ] Database integration for knowledge persistence
- [ ] API endpoint development
- [ ] Containerization (Docker) for deployment
- [ ] Load balancing and horizontal scaling

### Phase 6: Advanced Features
- [ ] Fact verification against sources
- [ ] Confidence scoring for responses
- [ ] Automatic knowledge base updates
- [ ] A/B testing for model variations

---

## 🤝 Contributing

We welcome contributions to improve this project!

### How to Contribute

1. **Fork** the repository
   ```bash
   git clone https://github.com/YOUR-USERNAME/Flexible-Multi-Agent-Knowledge-Platform.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-amazing-feature
   ```

3. **Make your changes** and commit
   ```bash
   git commit -m "Add your amazing feature"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-amazing-feature
   ```

5. **Open a Pull Request** with clear description of changes

### Contribution Guidelines

- Follow PEP 8 Python style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed
- Keep commit messages clear and descriptive

### Areas for Contribution

- Bug fixes and improvements
- Documentation enhancements
- Additional language support
- New retrieval strategies
- Performance optimizations
- Test coverage improvements

---

## 📜 License

This project is provided for **educational and research purposes**.

When a specific open-source license is selected for the repository, this section will be updated accordingly.

Suggested licenses:
- MIT License
- Apache 2.0
- GPL 3.0

---

## 👨‍💻 Author & Contact

**Developer:** Hamid4u-2026

**Project Type:** AI Diploma Graduation Project

**Email:** hamid4u.2026@gmail.com

**GitHub:** [Hamid4u-2026](https://github.com/Hamid4u-2026)

**Repository:** [Flexible-Multi-Agent-Knowledge-Platform](https://github.com/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform)

---

## 📚 References & Resources

### Documentation
- [FAISS Documentation](https://faiss.ai/)
- [Streamlit Official Docs](https://docs.streamlit.io/)
- [CrewAI Framework](https://docs.crewai.com/)
- [Sentence Transformers](https://www.sbert.net/)

### Tools & Platforms
- [LM Studio](https://lmstudio.ai/) - Local LLM Interface
- [Groq API](https://console.groq.com/) - Fast LLM API
- [Hugging Face Models](https://huggingface.co/models) - Pre-trained Models

### RAG & LLM Papers
- [Retrieval-Augmented Generation (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
- [FAISS Paper](https://arxiv.org/abs/1702.08734)
- [Sentence-BERT (Reimers & Gurevych, 2019)](https://arxiv.org/abs/1908.10084)

### Best Practices
- [RAG Best Practices](https://docs.llamaindex.ai/)
- [LLM Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Production LLM Deployment](https://huggingface.co/docs/inference-endpoints/index)

---

## 🔔 Latest Updates

- ✅ Core multi-agent architecture implemented
- ✅ FAISS vector indexing and retrieval completed
- ✅ Controlled web retrieval system deployed
- ✅ Evidence sufficiency assessment active
- ✅ Source attribution system operational
- ✅ LLM provider fallback mechanism working
- ✅ Multilingual query routing functional
- ✅ Streamlit interface deployed

---

## 📊 Project Statistics

- **Total Components:** 11 core modules
- **Agents:** 3 specialized agents
- **Supported Languages:** 2 (Arabic, English)
- **Web Sources:** 3 controlled SVU pages
- **Vector Index:** FAISS IndexFlatL2 (normalized)
- **Embedding Model:** BAAI/bge-small-en-v1.5
- **Local Model:** Qwen2.5-3B-Instruct (3B parameters)
- **Cloud Provider:** Groq API (GPT-OSS 20B)

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star!**

![GitHub stars](https://img.shields.io/github/stars/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform?style=social)

![GitHub forks](https://img.shields.io/github/forks/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform?style=social)

### Built with ❤️ for Education and Research

</div>

---

## 📝 Citation

If you use this project in your research or work, please cite:

```bibtex
@misc{flexible_multi_agent_2024,
  title={Flexible Multi-Agent Knowledge Management Platform},
  author={Hamid4u-2026},
  year={2024},
  howpublished={\url{https://github.com/Hamid4u-2026/Flexible-Multi-Agent-Knowledge-Platform}},
  note={AI Diploma Graduation Project}
}
```

---

**Last Updated:** September 2024

**Status:** Active Development

**Version:** 1.0.0