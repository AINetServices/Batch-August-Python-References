# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints require proper authentication through Supabase. The frontend handles authentication automatically.

## Endpoints

### Health Check
```http
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "Reference Checking System is running"
}
```

### Process Resume
```http
POST /api/process-resume
```

Processes an uploaded resume using the multi-agent workflow.

**Request Body:**
```json
{
  "resume_url": "https://storage.supabase.co/...",
  "role": "Software Engineer",
  "organization": "Tech Corp",
  "user_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "applicant_info": {
      "full_name": "John Doe",
      "email": "john@example.com",
      "current_position": "Senior Developer"
    },
    "references": [
      {
        "name": "Jane Smith",
        "email": "jane@company.com",
        "company": "Previous Corp",
        "relationship": "Direct Supervisor",
        "years_worked": "2020-2022"
      }
    ],
    "questions": [
      "How would you rate the candidate's technical skills?",
      "Can you describe their problem-solving abilities?"
    ]
  }
}
```

### Send Questions
```http
POST /api/send-questions
```

Sends approved questions to references.

**Request Body:**
```json
{
  "application_id": "uuid",
  "questions": [
    "How would you rate the candidate's technical skills?",
    "Can you describe their teamwork abilities?"
  ],
  "references": [
    {
      "name": "Jane Smith",
      "email": "jane@company.com",
      "company": "Previous Corp",
      "relationship": "Direct Supervisor",
      "years_worked": "2020-2022"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Questions sent to references"
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication required)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server-side error)

## Rate Limiting

The API implements basic rate limiting to prevent abuse. If you exceed the limits, you'll receive a `429 Too Many Requests` response.

## Multi-Agent Workflow

The `/api/process-resume` endpoint triggers a complex multi-agent workflow:

1. **Download Resume** - Fetches the file from Supabase storage
2. **Parse Resume** - Extracts text content from PDF/DOCX
3. **Extract Applicant** - Uses LLM to identify applicant details
4. **Extract References** - Finds potential references with context
5. **Build Vectorstore** - Creates semantic search index
6. **Fetch Questions** - Retrieves role-specific questions
7. **Finalize** - Prepares results for human review

Each step includes error handling and state management through LangGraph.