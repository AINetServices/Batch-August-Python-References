# Setup Guide

## Prerequisites

Before setting up the Reference Checking System, ensure you have:

- Node.js 18+ and npm
- Python 3.9+
- A Supabase account
- A Groq API key

## Step-by-Step Setup

### 1. Environment Setup

#### Frontend Environment
```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

#### Backend Environment
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
```

### 2. Database Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to the SQL Editor in your Supabase dashboard
3. Copy and execute the contents of `database/migrations/create_reference_system.sql`
4. Verify that the tables `applications`, `questions`, and `references` are created

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The backend API will be available at `http://localhost:8000`

### 5. Testing the System

1. Open the frontend in your browser
2. Create an account using the sign-up form
3. Upload a sample resume (PDF or DOCX)
4. Specify a role and organization
5. Monitor the processing status in the dashboard

## Troubleshooting

### Common Issues

1. **Supabase Connection Error**
   - Verify your Supabase URL and keys
   - Check that RLS policies are properly configured

2. **Groq API Error**
   - Ensure your Groq API key is valid
   - Check your API usage limits

3. **File Upload Issues**
   - Verify Supabase storage bucket is configured
   - Check file size limits (default: 10MB)

4. **Python Dependencies**
   - Use Python 3.9+ for best compatibility
   - Consider using a virtual environment

### Getting Help

If you encounter issues:
1. Check the console logs in both frontend and backend
2. Verify all environment variables are set correctly
3. Ensure all services (Supabase, Groq) are accessible
4. Create an issue in the GitHub repository with detailed error information