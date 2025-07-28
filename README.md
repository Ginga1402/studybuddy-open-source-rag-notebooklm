# 📚 StudyBuddy – Open Source RAG-Based AI Notebook and Google NotebookLM Alternative

**StudyBuddy is a free, open source alternative to Google NotebookLM that lets you chat with your documents, generate smart summaries, and organize knowledge with AI—all securely on your terms.**

## 🎯 Project Description

StudyBuddy is a comprehensive Retrieval-Augmented Generation (RAG) system that transforms static PDF documents into interactive learning experiences. Built with FastAPI and Streamlit, it leverages advanced AI technologies including HuggingFace embeddings, FAISS vector databases, and Large Language Models to create an intelligent document analysis platform.

### Technical Architecture
- **RAG Pipeline**: Implements state-of-the-art retrieval-augmented generation for accurate, context-aware responses
- **Vector Database**: Uses FAISS for efficient similarity search and document retrieval
- **Document Processing**: Converts PDFs to structured markdown using Docling for optimal text extraction
- **Embeddings**: Utilizes BGE-small-en-v1.5 embeddings with CUDA acceleration for fast processing
- **LLM Integration**: Powered by Gemma3:12b-it-q4_K_M via Ollama for high-quality text generation
- **Topic Modeling**: Implements LDA (Latent Dirichlet Allocation) for intelligent topic discovery

### Key Features
- **Document Ingestion**: Upload and process multiple PDFs into searchable knowledge bases
- **Interactive Q&A**: Chat with your documents using natural language queries
- **Smart Summaries**: Generate student-friendly summaries with key concepts and formulas
- **Visual Diagrams**: Create ASCII flowcharts and concept maps
- **Quiz Generation**: Automatically generate multiple-choice questions for self-assessment
- **FAQ Creation**: Extract frequently asked questions from document content
- **Topic Extraction**: Discover and organize important themes using AI-powered analysis
- **Analytics Dashboard**: Monitor usage patterns and system performance

## 📁 Project Structure

```
StudyBuddy/
├── configuration.py          # System configuration and model setup
├── FastAPI.py                # Main API server with all endpoints
├── streamlit_ui_fixed.py     # Enhanced web interface
├── ingestion.py              # PDF processing and vector store creation
├── QA_Rag.py                 # Question-answering RAG implementation
├── create_summary.py         # Document summarization module
├── create_diagram.py         # ASCII diagram generation
├── create_quiz.py            # Quiz generation system
├── create_faq.py             # FAQ extraction module
├── create_topics.py          # Topic modeling and extraction
├── Sample_outputs/           # Example outputs and demonstrations
├── Data/                     # PDF document storage directory
└── vector_store/             # FAISS vector database storage
```

## 🚀 Use Cases

### 📚 **Education & Learning**
- **Students**: Convert textbooks into interactive study materials with summaries, quizzes, and Q&A
- **Teachers**: Create educational content and assessments from curriculum documents
- **Researchers**: Analyze academic papers and extract key insights quickly

### 💼 **Professional & Business**
- **Knowledge Management**: Transform company documents into searchable knowledge bases
- **Training Materials**: Create interactive training modules from policy documents
- **Research & Development**: Analyze technical documentation and generate insights

### 🏥 **Specialized Domains**
- **Medical Education**: Process medical textbooks for case studies and exam preparation
- **Legal Research**: Analyze legal documents and extract relevant precedents
- **Technical Documentation**: Create interactive guides from complex technical manuals

---

## 🎬 Demo Video

See StudyBuddy in action! Watch our comprehensive demo showcasing all features:

[![▶️ Watch Demo](https://img.shields.io/badge/▶️_Watch_Demo-4CAF50?style=for-the-badgen&logoColor=white)](link-to-your-video-file.mp4)


### 📹 What's Covered in the Demo:
- **PDF Upload & Vector Store Creation**: See how easy it is to upload documents
- **Interactive Q&A**: Real-time question answering with source references
- **Content Generation**: Summaries, quizzes, diagrams, and FAQs in action
- **Analytics Dashboard**: Comprehensive usage tracking and metrics
- **User Interface**: Complete walkthrough of the enhanced Streamlit UI


---

## 🛠️ Installation Instructions

### Prerequisites
- Python 3.9+
- CUDA-compatible GPU (optional, for faster processing)
- 8GB+ RAM recommended

### Step 1: Clone Repository
```bash
git clone https://github.com/Ginga1402/StudyBuddy–OpenSource-NotebookLM-RAG-Based-AI.git
cd studybuddy
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Additional Requirements
```bash
pip install -r streamlit_requirements.txt
```

### Step 4: Set Up Ollama (LLM Backend)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull gemma3:12b-it-q4_K_M
```

### Step 5: Configure Paths
Update the paths in `configuration.py` to match your system:
```python
DIRECTORY_PATH = "your/path/to/Data"
VECTORSORE_PATH = "your/path/to/vector_store"
```

## 📖 Usage

### Starting the Application

1. **Start the FastAPI Server**:
```bash
python FastAPI.py
```
The API will be available at `http://localhost:9000`

2. **Launch the Streamlit Interface**:
```bash
streamlit run streamlit_ui_fixed.py
```
The web interface will open at `http://localhost:8501`

### Basic Workflow

1. **Create Vector Store**: Upload PDF files and create a searchable knowledge base
2. **Generate Content**: Use various features to create summaries, quizzes, diagrams, and FAQs
3. **Interactive Q&A**: Ask questions about your documents and get contextual answers
4. **Download Results**: Save generated content as text files for offline use
5. **Monitor Analytics**: Track usage patterns and system performance

### API Endpoints

- `POST /create-vectorstore/` - Create vector store from PDFs
- `POST /QA-Guide/` - Question-answering with RAG
- `POST /generate-summary/` - Generate document summaries
- `POST /generate-diagram/` - Create ASCII diagrams
- `POST /generate-quiz/` - Generate multiple-choice quizzes
- `POST /generate-FAQ/` - Create frequently asked questions
- `POST /generate-important-topics/` - Extract key topics
- `GET /heartbeat` - Health check endpoint
- `GET /metrics` - System usage metrics

## 🔧 Technologies Used

| Technology | Description | Link |
|------------|-------------|------|
| **FastAPI** | High-performance web framework for building APIs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| **Streamlit** | Framework for creating interactive web applications | [streamlit.io](https://streamlit.io/) |
| **LangChain** | Framework for developing LLM-powered applications | [langchain.com](https://www.langchain.com/) |
| **FAISS** | Library for efficient similarity search and clustering | [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss) |
| **HuggingFace Transformers** | State-of-the-art ML models and embeddings | [huggingface.co](https://huggingface.co/) |
| **Ollama** | Local LLM runtime for running language models | [ollama.ai](https://ollama.ai/) |
| **Docling** | Advanced document processing and conversion | [github.com/DS4SD/docling](https://github.com/DS4SD/docling) |
| **NLTK** | Natural language processing toolkit | [nltk.org](https://www.nltk.org/) |
| **Gensim** | Topic modeling and document similarity analysis | [radimrehurek.com/gensim](https://radimrehurek.com/gensim/) |
| **PyTorch** | Deep learning framework with CUDA support | [pytorch.org](https://pytorch.org/) |
| **Pandas** | Data manipulation and analysis library | [pandas.pydata.org](https://pandas.pydata.org/) |
| **Pydantic** | Data validation using Python type annotations | [pydantic.dev](https://pydantic.dev/) |

## 🤝 Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If you find StudyBuddy useful, please consider giving it a star ⭐ on GitHub!
