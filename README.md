# Reference Checking System
A comprehensive reference checking system built with React, TypeScript, Supabase, and Python with advanced AI capabilities using LangGraph multi-agents.
## Features
- 🔐 **Complete Authentication System** - Sign in, sign out, and password reset with Supabase ✅
- 📄 **Resume Upload & Processing** - Drag-and-drop interface with AI-powered extraction ✅
- 🤖 **Multi-Agent AI Workflow** - LangGraph-based system for intelligent resume analysis ✅
- 👥 **Reference Extraction** - Automatically identify potential references from resumes ✅
- ❓ **Question Management** - Role-specific questions with human-in-the-loop approval ✅
- 📊 **Real-time Dashboard** - Track application status and manage references 
- 🔍 **Advanced RAG System** - Vector-based semantic search and document analysis

## Quick Start

### Prerequisites (make sure they are installed)
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- Groq API key

## Setup
1. There are 2 steps to setup this project
The frontend and the backend

### Frontend Setup
1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your Supabase credentials:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
```

4. Run the development server:
```bash
npm run dev
```

5. The website will not work till backend is also setup, but ensure it you see something like this:
```
  VITE v5.4.8  ready in 195 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```
### Backend Setup
1. Navigate to the Python backend in a terminal:
```bash
cd python_backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Update `python_backend/.env` with your credentials:
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

6. Run the Python backend:
```bash
python run.py
```

### Database Setup

1. Run the Supabase migration to create the required tables:
```sql
-- Execute the migration file in your Supabase SQL editor
-- File: supabase/migrations/create_reference_system.sql
```

2. Enable Row Level Security (RLS) policies as defined in the migration.

## Architecture

### Multi-Agent Workflow

The system uses LangGraph to orchestrate a multi-agent workflow:

1. **Download Resume Node** - Fetches and processes uploaded files
2. **Parse Resume Node** - Extracts and chunks text content
3. **Extract Applicant Node** - Identifies applicant details using LLM
4. **Extract References Node** - Finds potential references with context
5. **Build Vectorstore Node** - Creates semantic search capabilities
6. **Fetch Questions Node** - Retrieves role-specific questions
7. **Finalize Node** - Prepares results for human review

### Custom Tools

- **ResumeParserTool** - PDF/DOCX text extraction
- **ReferenceExtractorTool** - AI-powered reference identification
- **QuestionFetcherTool** - Database integration for questions
- **VectorStoreTool** - Semantic search operations
- **DatabaseUpdateTool** - Supabase data management

## API Endpoints

- `POST /api/process-resume` - Process uploaded resume with AI workflow
- `POST /api/send-questions` - Send approved questions to references
- `GET /health` - Health check endpoint

## Database Schema

### Tables
- **applications** - Job applications with extracted data
- **questions** - Predefined questions by role and organization
- **references** - Reference contacts and their responses

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Environment Variables

### Frontend (.env)
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend (python_backend/.env)
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email your-email@example.com or create an issue in this repository.



## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Supabase** for authentication and database
- **Lucide React** for icons
- **Vite** for development and building

### Backend
- **Python FastAPI** for API endpoints
- **LangGraph** for multi-agent workflows
- **LangChain** with Groq LLM integration
- **ChromaDB** for vector storage
- **Supabase** for database operations
- **HuggingFace Embeddings** for semantic search
