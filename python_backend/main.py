"""
Main FastAPI application for the Reference Checking System.
Handles resume processing, reference extraction, and question management.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from dotenv import load_dotenv

from agents.reference_checking_workflow import ReferenceCheckingWorkflow
from services.supabase_service import SupabaseService


load_dotenv()

app = FastAPI(title="Reference Checking System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
workflow = ReferenceCheckingWorkflow()
db_service = SupabaseService()

class ProcessResumeRequest(BaseModel):
    resume_url: str
    role: str
    organization: str
    user_id: str

class SendQuestionsRequest(BaseModel):
    application_id: str
    questions: List[str]
    references: List[Dict[str, Any]]

@app.get("/")
async def root():
    return {"message": "Reference Checking System API", "version": "1.0.0"}

@app.post("/api/process-resume")
async def process_resume(request: ProcessResumeRequest):
    """
    Process uploaded resume using the multi-agent workflow.
    Extracts applicant details and references, then updates the database.
    """
    try:
        # Run the multi-agent workflow
        result = await workflow.run_workflow(
            resume_url=request.resume_url,
            role=request.role,
            organization=request.organization
        )
        
        # Update application in dzatabase
        await db_service.update_application(
            user_id=request.user_id,
            role=request.role,
            organization=request.organization,
            extracted_data=result,
            status="extracted"
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/api/send-questions")
async def send_questions(request: SendQuestionsRequest):
    """
    Send approved questions to references via email.
    Creates reference records in the database.
    """
    try:
        # Create reference records
        for ref in request.references:
            await db_service.create_reference(
                application_id=request.application_id,
                reference_data=ref,
                questions=request.questions
            )
        
        # Here you would integrate with an email service
        # For now, we'll just update the application status
        await db_service.update_application_status(
            application_id=request.application_id,
            status="sent"
        )
        
        return {"success": True, "message": "Questions sent to references"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending questions: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Reference Checking System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)