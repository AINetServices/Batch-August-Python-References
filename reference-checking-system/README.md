# Reference Checking System

A comprehensive AI-powered reference checking system built with React, TypeScript, Python, and Supabase. This system automates the process of extracting references from resumes and managing reference check workflows with human-in-the-loop approval.

## 🚀 Features

- **Complete Authentication System** - Sign in, sign out, and password reset with Supabase
- **Resume Upload & Processing** - Drag-and-drop interface with AI-powered extraction
- **Multi-Agent AI Workflow** - LangGraph-based system for intelligent resume analysis
- **Reference Extraction** - Automatically identify potential references from resumes
- **Question Management** - Role-specific questions with human-in-the-loop approval
- **Real-time Dashboard** - Track application status and manage references
- **Advanced RAG System** - Vector-based semantic search and document analysis

## 🏗️ Architecture

```
reference-checking-system/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities and configurations
│   │   └── ...
│   ├── package.json
│   └── ...
├── backend/                 # Python FastAPI backend
│   ├── agents/             # LangGraph multi-agent system
│   ├── services/           # External service integrations
│   ├── requirements.txt
│   └── main.py
├── database/               # Supabase migrations and schema
│   └── migrations/
└── docs/                   # Documentation
```

## 🛠️ Tech Stack

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

### Database
- **Supabase PostgreSQL** with Row Level Security
- **Comprehensive schema** for applications, references, and questions

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- Groq API key

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/reference-checking-system.git
cd reference-checking-system
```

### 2. Frontend Setup
```bash
cd frontend
npm install

# Copy environment template
cp .env.example .env

# Update .env with your Supabase credentials
# VITE_SUPABASE_URL=your_supabase_url
# VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Start development server
npm run dev
```

### 3. Backend Setup
```bash
cd ../backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Update .env with your credentials
# GROQ_API_KEY=your_groq_api_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_SERVICE_KEY=your_supabase_service_key

# Run the backend
python run.py
```

### 4. Database Setup
1. Create a new Supabase project
2. Run the migration file in your Supabase SQL editor:
   ```sql
   -- Execute: database/migrations/create_reference_system.sql
   ```
3. Enable Row Level Security policies as defined in the migration

## 🤖 Multi-Agent Workflow

The system uses LangGraph to orchestrate a sophisticated multi-agent workflow:

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

## 📊 Database Schema

### Core Tables
- **applications** - Job applications with extracted data and status tracking
- **questions** - Predefined questions by role and organization
- **references** - Reference contacts and their responses

### Security
- Row Level Security (RLS) enabled on all tables
- User-based access control policies
- Secure API key management

## 🔧 API Endpoints

- `POST /api/process-resume` - Process uploaded resume with AI workflow
- `POST /api/send-questions` - Send approved questions to references
- `GET /health` - Health check endpoint

## 🌟 Key Features Explained

### Resume Processing
1. User uploads resume (PDF/DOCX) with role and organization details
2. Multi-agent system extracts applicant information and references
3. Vector store created for semantic search capabilities
4. Results presented for human review and approval

### Reference Management
1. Extracted references displayed with relationship context
2. Role-specific questions fetched from database
3. Human-in-the-loop approval for question customization
4. Automated distribution to reference contacts

### Dashboard & Tracking
1. Real-time status updates for each application
2. Visual progress indicators and statistics
3. Comprehensive application management interface
4. Reference response tracking and management

## 🔒 Environment Variables

### Frontend (.env)
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend (.env)
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## 🚀 Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

### Backend (Railway/Heroku)
```bash
cd backend
# Deploy with your preferred platform
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, create an issue in this repository or contact the development team.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for multi-agent workflows
- Powered by [Groq](https://groq.com/) for fast LLM inference
- Database and auth by [Supabase](https://supabase.com/)
- UI components styled with [Tailwind CSS](https://tailwindcss.com/)