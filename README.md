# LangGraph with RAG

A question-answering system combining LangGraph and RAG (Retrieval-Augmented Generation), specifically designed to handle queries about heavy motorcycles and traffic regulations.

## System Architecture

![Flowchart](docs/images/Flowchart.jpg)

### Main Flow

1. **Question Assessment (Grade Question)**
   - Evaluates whether questions are appropriate (filters inappropriate content)
   - If appropriate, proceeds to routing stage

2. **Question Routing (Route Question)**
   - Determines data source based on question content:
     - Vectorstore: For traffic regulation queries
     - Web Search: For general queries
     - Plain Answer: Direct LLM response

3. **Data Retrieval (Retrieval)**
   - Vectorstore: Retrieves relevant documents from local vector database
   - Web Search: Uses Tavily for web information search

4. **Retrieval Grading (Retrieval Grader)**
   - Evaluates retrieval result relevance
   - Supports retry mechanism (maximum once)

5. **Answer Generation (RAG Responder)**
   - Uses GPT-4o-mini with vector database for answer generation
   - Includes hallucination detection and quality assessment

## Project Structure

```
LangGraph_with_RAG/
├── config/             # Configuration files
│   └── config.py      # Environment variable setup
├── data/              # Data processing
│   └── data.py        # PDF loading and vector database
├── models/            # Data models
│   └── state.py       # State definitions
├── nodes/             # Workflow nodes
│   ├── generators.py  # Answer generation
│   ├── graders.py     # Grading and routing
│   └── retrievers.py  # Data retrieval
├── services/          # Core services
│   ├── embeddings.py  # Google Embeddings
│   ├── llm.py        # LLM configuration
│   └── llm_model.py  # LLM grading models
└── docs/             # Documentation
    └── images/       # Image resources
```

## Models and Services Used

1. **Language Model**
   - OpenAI GPT-4o-mini

2. **Vector Embeddings**
   - Google Generative AI Embeddings (models/embedding-001)

3. **External Services**
   - Tavily Search API
   - Google AI API
   - OpenAI API

## Installation and Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Environment variables setup (.env):
```
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
```

## Usage

```python
from main import run_query

# Execute query
question = "What are the regulations for license renewal?"
answer = run_query(question)
print(answer)
```

## Key Features

1. **Intelligent Routing**
   - Automatically selects the most suitable data source
   - Supports multiple data source integration

2. **Quality Control**
   - Content filtering
   - Relevance scoring
   - Hallucination detection
   - Answer quality assessment

3. **Error Handling**
   - Intelligent retry mechanism
   - Fallback options
