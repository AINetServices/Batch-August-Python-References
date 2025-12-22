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

## Quick Start (After setup)

**If this is your first time, please skip this section and go to Prequisites and setup the app and environment**

You are going to need two terminals for this app, one for the frontend and one for the backend

1. First in a new terminal start backend using python

```bash
python python/python_backend/run.py
```

```example output
INFO:     Started server process [19240]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**_look for application startup complete thats when you know its ready_**

2. Second open a second terminal and run front end using npm

```bash
npm run dev
```

Expected output: should be like this

```example
VITE v5.4.8  ready in 195 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**_control and click to the local host link provided to start your app_**

### Keep in mind

The above steps can be done in any order and simulataneously, the app will work regardless as long as you get both the example outputs that will indicate the app is ready to use.

# Full setup (if first time)

## Prerequisites (make sure they are installed)

- Node.js 18+ and npm
- Python 3.9+ (DO NOT USE LATEST PYTHON <3.14 NOT COMPATIABLE)
- Supabase account
- Groq API key
- Git

## Setup

Once you have prequisites ready and installed, setup the following
Three Core functions required for this app to function:

1. Frontend Setup
2. Backend Setup
3. Database Setup

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

**_Note this might take a long time_**

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

#### In order to setup the database first we must run the program and create a user

**These steps might require some navigation. as steps and interfaces can change overtime**

1. go to supabase.com
2. Create an account > start an organization > start a project name it AINET (or anything)
   Eventually a page should appear showing project overview
3. On the left hand side toolbar go to **storage**
4. Click new bucket or create bucket and call it **_resumes_**
5. For development purposes ensure "public bucket" is enabled and click create
6. Next On the left-hand sidebar look for "SQL Editor"
   A text editor should show up
7. Now you need to paste several scripts that will set up the database
   - Paste the script into the editor window and click on the Run button (control + enter is also a shortcut)
   - For every script ensure you use a new editor window to keep track of the scripts (this can be done creating a script tab at the top near the editor window usually a + icon)
   - Ensure you do not get any error outputs, look for success, or No rows returned or anything similar when running otherwise try and debug.

### Script #1 Core Tables

Copy and Paste the following script into the text editor and

```

-- Applications table to store job applications and extracted resume data
CREATE TABLE IF NOT EXISTS applications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  resume_url text NOT NULL,
  role text NOT NULL,
  organization text NOT NULL,
  extracted_data jsonb DEFAULT '{}',
  status text DEFAULT 'processing' CHECK (status IN ('processing', 'extracted', 'approved', 'sent', 'completed')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Questions table to store predefined questions by role and organization
CREATE TABLE IF NOT EXISTS questions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  role text NOT NULL,
  organization text NOT NULL,
  questions jsonb NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE(role, organization)
);

-- References table to store reference contacts and their responses
CREATE TABLE IF NOT EXISTS SOURCE_REFERENCES (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id uuid REFERENCES applications(id) ON DELETE CASCADE NOT NULL,
  name text NOT NULL,
  email text NOT NULL,
  company text NOT NULL,
  relationship text NOT NULL,
  years_worked text NOT NULL,
  questions_sent jsonb DEFAULT '[]',
  responses jsonb DEFAULT '{}',
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'responded', 'overdue')),
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE SOURCE_REFERENCES ENABLE ROW LEVEL SECURITY;

-- RLS Policies for applications
CREATE POLICY "Users can manage their own applications"
  ON applications
  FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for questions (read-only for authenticated users)
CREATE POLICY "Authenticated users can read questions"
  ON questions
  FOR SELECT
  TO authenticated
  USING (true);

-- RLS Policies for references (access through applications)
CREATE POLICY "Users can manage references for their applications"
  ON SOURCE_REFERENCES
  FOR ALL
  TO authenticated
  USING (
    application_id IN (
      SELECT id FROM applications WHERE user_id = auth.uid()
    )
  )
  WITH CHECK (
    application_id IN (
      SELECT id FROM applications WHERE user_id = auth.uid()
    )
  );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for applications table
CREATE TRIGGER update_applications_updated_at
  BEFORE UPDATE ON applications
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample questions for common roles
INSERT INTO questions (role, organization, questions) VALUES
('Software Engineer', 'Tech Corp', '[
  "How would you rate the candidate''s technical skills and coding abilities?",
  "Can you describe a challenging project they worked on and how they handled it?",
  "How did they collaborate with team members and handle feedback?",
  "What are their strongest technical competencies?",
  "Would you recommend them for a senior software engineering position?"
]'),
('Marketing Manager', 'Digital Agency', '[
  "How would you evaluate their campaign management and strategic thinking?",
  "Can you provide examples of successful marketing initiatives they led?",
  "How did they handle budget management and ROI optimization?",
  "What are their strengths in team leadership and client relations?",
  "Would you hire them again for a marketing leadership role?"
]'),
('Data Scientist', 'Analytics Inc', '[
  "How would you assess their analytical and statistical modeling skills?",
  "Can you describe their experience with machine learning projects?",
  "How did they communicate complex findings to non-technical stakeholders?",
  "What programming languages and tools did they excel at?",
  "Would you recommend them for a senior data science position?"
]');

```

    ***Expected output for this is: Success No Rows Returned***

### Script Number #2 Authentication policies

```

-- Allow authenticated users to upload files
CREATE POLICY "Allow authenticated upload to resumes"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'resumes');

-- Allow authenticated users to read files
CREATE POLICY "Allow authenticated read from resumes"
ON storage.objects
FOR SELECT
TO authenticated
USING (bucket_id = 'resumes');

-- Allow authenticated users to update files
CREATE POLICY "Allow authenticated update to resumes"
ON storage.objects
FOR UPDATE
TO authenticated
USING (bucket_id = 'resumes');

-- Allow authenticated users to delete files
CREATE POLICY "Allow authenticated delete from resumes"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'resumes');

```

### Script Number #2 Authentication policies

```



```

# Architecture

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
