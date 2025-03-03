# LangGraph with RAG

A question-answering system combining LangGraph and RAG (Retrieval-Augmented Generation), specifically designed to handle queries about heavy motorcycles and traffic regulations.

## System Architecture

```mermaid
graph TD
    Question[Question] --> GradeQuestion{Grade Question}
    
    GradeQuestion -->|No| NoAnswer[No Answer]
    GradeQuestion -->|Yes| RouteQuestion{Route Question}
    
    RouteQuestion -->|Vectorstore| Retrieve[Retrieve]
    RouteQuestion -->|Web Search| WebSearch[Web Search]
    RouteQuestion -->|Plain Answer| PlainAnswer[Plain Answer]
    
    Retrieve --> RetrievalGrader[Retrieval Grader]
    WebSearch --> RetrievalGrader
    
    RetrievalGrader --> RouteRetrieval{Route Retrieval}
    
    RouteRetrieval -->|Empty & web_retry < 1| UpdateWebSearch[Update Web Search Count]
    RouteRetrieval -->|Empty & web_retry >= 1| PlainAnswer
    RouteRetrieval -->|Non-Empty| RAGResponder[RAG Responder]
    
    UpdateWebSearch --> WebSearch
    
    RAGResponder --> HallucinationGrader{Hallucination Check}
    
    HallucinationGrader -->|No| AnswerGrader{Answer Quality}
    HallucinationGrader -->|Yes & rag_retry < 1| UpdateRAGGenerate[Update RAG Count]
    HallucinationGrader -->|Yes & rag_retry >= 1| PlainAnswer
    
    UpdateRAGGenerate --> RAGResponder
    
    AnswerGrader -->|Yes| Answer[Answer]
    AnswerGrader -->|No & web_retry < 1| UpdateWebSearch
    AnswerGrader -->|No & web_retry >= 1| PlainAnswer
    
    PlainAnswer --> Answer

    style GradeQuestion fill:#ff69b4
    style RouteQuestion fill:#ff69b4
    style RouteRetrieval fill:#ff69b4
    style HallucinationGrader fill:#ff69b4
    style AnswerGrader fill:#ff69b4
    
    style Retrieve fill:#98fb98
    style WebSearch fill:#98fb98
    style RetrievalGrader fill:#98fb98
    style RAGResponder fill:#98fb98
    style UpdateWebSearch fill:#98fb98
    style UpdateRAGGenerate fill:#98fb98
    style PlainAnswer fill:#98fb98
    
    style Question fill:#fff
    style NoAnswer fill:#fff
    style Answer fill:#fff
```

### Main Flow

1. **Question Assessment (Grade Question)**
   - Evaluates whether questions are appropriate (filters inappropriate content)
   - If appropriate, proceeds to routing stage

2. **Question Routing (Route Question)**
   - Determines data source based on question content:
     - Vectorstore: For traffic regulation queries
     - Web Search: For general queries
     - Plain Answer: Direct LLM response

3. **Data Retrieval & Processing**
   - Vectorstore/Web Search retrieval
   - Retrieval grading with retry mechanism
   - RAG response generation with quality checks

4. **Quality Control**
   - Web search retry count tracking
   - RAG generation retry count tracking
   - Multiple fallback options to ensure quality

## Project Structure

```
LangGraph_with_RAG/
├── frontend/           # React frontend application
│   ├── public/        # Static files
│   └── src/           # React source code
├── config/            # Configuration files
│   └── config.py      # Environment variable setup
├── data/              # Data processing
│   └── data.py        # PDF loading and vector database
├── models/            # Data models
│   └── state.py       # State definitions
├── nodes/             # Workflow nodes
│   ├── generators.py  # Answer generation
│   ├── graders.py     # Grading and routing
│   └── retrievers.py  # Data retrieval
└── services/          # Core services
    ├── embeddings.py  # Google Embeddings
    ├── llm.py        # LLM configuration
    └── llm_model.py  # LLM grading models
```

## Installation and Setup

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Environment variables setup (.env):
```
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
TAVILY_API_KEY=your-tavily-api-key
```

## Database Setup

### Using Docker (Recommended)
1. Start the database using Docker Compose:
```bash
cd Docker
docker-compose up -d postgres_memory
```

2. Environment variables setup (.env):
```
DB_URI="postgresql://postgres:postgres@localhost:5432/postgres"
```

## Running the Application

### Using Docker
1. Start all services:
```bash
cd Docker
docker-compose up
```

### Manual Setup
1. Start the backend server:
```bash
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

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

4. **User Interface**
   - React-based frontend
   - Responsive design
   - Real-time error handling
   - Loading state indicators

## Technologies Used

### Backend
- FastAPI
- LangGraph
- OpenAI GPT
- Google AI
- Tavily Search API

### Frontend
- React
- Create React App
- Modern CSS
- Fetch API
