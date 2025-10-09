"""
Main FastAPI application for the Reference Checking System.
Handles resume processing, reference extraction, and question management.
"""

import os
<<<<<<< HEAD
import re
=======
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from dotenv import load_dotenv
<<<<<<< HEAD
from io import BytesIO
import pdfplumber
import requests
import re


from agents.reference_checking_workflow import ReferenceCheckingWorkflow
from services.supabase_service import SupabaseService
# Add this import at the top of your workflow file
from .tools.email_tools import create_reference_emailer_tool

class ReferenceCheckingWorkflow:
    def __init__(self):
        # ... existing code ...
        
        # Initialize email tool
        self.email_tool = create_reference_emailer_tool()
        
        # ... rest of your init code ...

    # Add a new node to your workflow for sending emails
    async def _send_emails_node(self, state: WorkflowState) -> WorkflowState:
        """Send reference check emails to all references"""
        try:
            if state["status"] == "error":
                return state

            # Only send emails if we have references and questions
            if state.get("references") and state.get("questions"):
                email_results = self.email_tool(
                    references=state["references"],
                    applicant_info=state["applicant_info"],
                    role=state["role"],
                    organization=state["organization"],
                    questions=state["questions"]
                )
                
                state["email_results"] = email_results
                state["status"] = "emails_sent"
                print(f"✅ Emails sent: {email_results['total_successful']}/{email_results['total_attempted']} successful")
            else:
                print("⚠️ No references or questions available for email sending")
                state["email_results"] = {"sent": [], "failed": [], "total_attempted": 0, "total_successful": 0}
                state["status"] = "emails_skipped"

        except Exception as e:
            print(f"⚠️ Email sending failed, but continuing: {str(e)}")
            state["email_results"] = {"sent": [], "failed": [], "total_attempted": 0, "total_successful": 0}
            state["status"] = "emails_failed"

        return state

    # Update your workflow graph to include the email node
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        # Add all your existing nodes...
        workflow.add_node("download_resume", self._download_resume_node)
        workflow.add_node("parse_resume", self._parse_resume_node)
        workflow.add_node("extract_applicant", self._extract_applicant_node)
        workflow.add_node("extract_references", self._extract_references_node)
        workflow.add_node("build_vectorstore", self._build_vectorstore_node)
        workflow.add_node("fetch_questions", self._fetch_questions_node)
        
        # Add the new email node
        workflow.add_node("send_emails", self._send_emails_node)
        workflow.add_node("finalize", self._finalize_node)

        # Update edges to include email node
        workflow.add_edge("fetch_questions", "send_emails")
        workflow.add_edge("send_emails", "finalize")
        workflow.add_edge("finalize", END)

        workflow.set_entry_point("download_resume")
        return workflow.compile()
=======

from agents.reference_checking_workflow import ReferenceCheckingWorkflow
from services.supabase_service import SupabaseService
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517

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

<<<<<<< HEAD
# Add this at the top of your main.py after imports
print("🔍 Environment Variables Check:")
print(f"   SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Not set'}")
print(f"   SUPABASE_SERVICE_KEY: {'✅ Set' if os.getenv('SUPABASE_SERVICE_KEY') else '❌ Not set'}")
print(f"   GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set'}")

=======
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517
# Initialize services
workflow = ReferenceCheckingWorkflow()
db_service = SupabaseService()

class ProcessResumeRequest(BaseModel):
    resume_url: str
    role: str
    organization: str
    user_id: str
<<<<<<< HEAD
    application_id: str
=======
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517

class SendQuestionsRequest(BaseModel):
    application_id: str
    questions: List[str]
    references: List[Dict[str, Any]]

<<<<<<< HEAD
def parse_reference_data(reference_text):
    """Parse the reference text into structured data for the database"""
    print(f"🔍 Parsing reference text: {reference_text}")
    
    name = ""
    email = ""
    phone_number = ""
    company = ""
    relationship = ""

    try:
        # Clean and split the reference text
        reference_text = reference_text.strip()
        
        # Extract email using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, reference_text)
        if email_match:
            email = email_match.group()
            # Remove email from text for cleaner parsing
            reference_text = re.sub(email_pattern, '', reference_text).strip()
        
        # Extract phone number using regex
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, reference_text)
        if phone_match:
            phone_number = phone_match.group().strip()
            # Remove phone from text for cleaner parsing
            reference_text = re.sub(phone_pattern, '', reference_text).strip()
        
        # Split by common separators
        parts = []
        for separator in ['|', ',', ';', '-']:
            if separator in reference_text:
                parts = [part.strip() for part in reference_text.split(separator) if part.strip()]
                break
        
        if not parts:
            parts = [reference_text]
        
        # The first part is typically the name and possibly company
        if parts:
            name_company_part = parts[0]
            
            # Check if name contains company (common pattern: "Name, Company")
            if ',' in name_company_part:
                name_company_split = name_company_part.split(',', 1)
                name = name_company_split[0].strip()
                company = name_company_split[1].strip()
                
                # Clean company from any remaining email/phone artifacts
                company_words = []
                for word in company.split():
                    if '@' in word or any(char.isdigit() for char in word):
                        continue
                    company_words.append(word)
                company = ' '.join(company_words).strip()
            else:
                name = name_company_part
                company = ""
        
        # Process remaining parts for relationship and additional info
        for part in parts[1:]:
            part_lower = part.lower()
            if any(keyword in part_lower for keyword in ['relationship', 'relation', 'worked', 'manager', 'supervisor', 'colleague']):
                relationship = part.strip()
            elif not company and len(part) > 2:  # Use as company if not already set
                company = part.strip()
        
        # Final cleanup
        if '@' in name:
            name_parts = name.split()
            name = ' '.join([part for part in name_parts if '@' not in part]).strip()
        
        # Validate required fields
        if not name:
            name = "Unknown Reference"
            print("⚠️  Name not found in reference")
        
        if not email:
            print("⚠️  Email not found in reference")
        
        if not phone_number:
            print("⚠️  Phone number not found in reference")
        
        parsed_data = {
            'name': name,
            'email': email,
            'phone_number': phone_number,
            'company': company,
            'relationship': relationship
        }
        
        print(f"✅ Parsed reference data: {parsed_data}")
        return parsed_data

    except Exception as e:
        print(f"❌ Error parsing reference '{reference_text}': {e}")
        return {
            'name': reference_text[:100] if reference_text else "Unknown Reference",
            'email': '',
            'phone_number': '',
            'company': '',
            'relationship': ''
        }

def validate_extracted_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that we have the minimum required data"""
    print("🔍 Validating extracted data...")
    
    if not result:
        return {"error": "No data extracted from resume"}
    
    # Get references or default to empty list
    references = result.get('references', [])
    
    # Don't fail if references are empty - this is common
    if not references:
        print("⚠️ No references found in resume - this is normal for some resumes")
        result['validated_references'] = []
        result['validation_summary'] = {
            'total_references': 0,
            'with_email': 0,
            'with_phone': 0,
            'missing_info': 0
        }
        return result
    
    # If we have references, validate them
    valid_references = []
    for i, ref in enumerate(references):
        if not ref or not ref.strip():
            continue
            
        parsed_ref = parse_reference_data(ref)
        
        # Check minimum requirements
        if not parsed_ref.get('name') or parsed_ref.get('name') == 'Unknown Reference':
            print(f"⚠️ Reference {i+1} missing valid name: {ref}")
            continue
            
        valid_references.append(parsed_ref)
    
    # Update result with validated references
    result['validated_references'] = valid_references
    result['validation_summary'] = {
        'total_references': len(valid_references),
        'with_email': sum(1 for ref in valid_references if ref.get('email')),
        'with_phone': sum(1 for ref in valid_references if ref.get('phone_number')),
        'missing_info': len(valid_references) - sum(1 for ref in valid_references if ref.get('email') or ref.get('phone_number'))
    }
    
    print(f"📊 Validation Results:")
    print(f"   Total valid references: {len(valid_references)}")
    
    return result

=======
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517
@app.get("/")
async def root():
    return {"message": "Reference Checking System API", "version": "1.0.0"}

@app.post("/api/process-resume")
async def process_resume(request: ProcessResumeRequest):
<<<<<<< HEAD
    try:
        print(f"🚀 Starting AI-powered resume processing for application {request.application_id}")
        print(f"📄 Resume URL: {request.resume_url}")

        # Step 1️⃣ Run AI workflow
        ai_result = None
        try:
            print("🤖 Running Groq AI workflow...")
            ai_result = await workflow.run_workflow(
                resume_url=request.resume_url,
                role=request.role,
                organization=request.organization
            )
            print(f"✅ AI workflow result: {ai_result}")
        except Exception as ai_error:
            print(f"⚠️ AI workflow failed: {ai_error}")
            ai_result = {}

        # Step 2️⃣ Download the resume
        response = requests.get(request.resume_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download resume")

        # Step 3️⃣ Extract text for fallback parsing
        text = ""
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            print("⚠️ No readable text found in resume.")
            raise HTTPException(status_code=400, detail="No text found in resume")

        # Step 4️⃣ Regex fallback extraction
        print("🔍 Running regex fallback extractor...")
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        phone_pattern = re.compile(r"(\+?\d[\d\s-]{7,15})")
        name_pattern = re.compile(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)")

        email_match = email_pattern.search(text)
        phone_match = phone_pattern.search(text)
        name_match = name_pattern.search(text)

        fallback_data = {
            "name": name_match.group(0) if name_match else "",
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
        }

        print(f"🧩 Fallback extracted data: {fallback_data}")

        # Step 5️⃣ Merge AI + fallback results
        extracted_data = {
            "ai_result": ai_result,
            "fallback": fallback_data,
            "final": {
                "name": ai_result.get("name") or fallback_data["name"],
                "email": ai_result.get("email") or fallback_data["email"],
                "phone": ai_result.get("phone") or fallback_data["phone"],
                "references": ai_result.get("references", []),
                "resume_url": request.resume_url
            }
        }

        print(f"🧠 Final merged extraction: {extracted_data['final']}")

        # Step 6️⃣ Determine status and extraction flags
        status = "extracted" if any(extracted_data['final'].values()) else "processing"
        
        # Calculate extraction flags for frontend
        extracted_keys = []
        if extracted_data['final'].get('name'):
            extracted_keys.append('name')
        if extracted_data['final'].get('email'):
            extracted_keys.append('email')
        if extracted_data['final'].get('phone'):
            extracted_keys.append('phone')
        if extracted_data['final'].get('references'):
            extracted_keys.append('references')

        has_extracted_data = len(extracted_keys) > 0
        extracted_data_keys_str = ','.join(extracted_keys) if extracted_keys else "none"

        print(f"🏷️ Extraction flags - has_extracted_data: {has_extracted_data}, keys: {extracted_data_keys_str}")

        # Step 7️⃣ Save to Supabase with extraction flags
        update_result = db_service.update_application(
            application_id=request.application_id,
            extracted_data=extracted_data['final'],
            role=request.role,
            organization=request.organization,
            user_id=request.user_id,
            status=status,
            has_extracted_data=has_extracted_data,
            extracted_data_keys=extracted_data_keys_str
        )

        print(f"✅ Application updated in Supabase: {update_result}")

        return {
            "success": True,
            "application_id": request.application_id,
            "status": status,
            "ai_used": bool(ai_result),
            "has_extracted_data": has_extracted_data,
            "extracted_data_keys": extracted_data_keys_str,
            "data": extracted_data['final']
        }

    except Exception as e:
        print(f"💥 Error processing resume: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


# 🔍 DEBUG ENDPOINTS
@app.get("/debug/applications")
async def debug_applications(user_id: str = None):
    """Debug endpoint to check applications in database"""
    try:
        if user_id:
            response = await db_service.supabase.table('applications')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
        else:
            response = await db_service.supabase.table('applications')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()

        return {
            "success": True,
            "count": len(response.data),
            "applications": response.data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/candidate-references")
async def debug_candidate_references(candidate_id: str = None):
    """Debug endpoint to check candidate_references in database"""
    try:
        if candidate_id:
            response = db_service.supabase.table('candidate_references')\
                .select('*')\
                .eq('candidate_id', candidate_id)\
                .execute()
        else:
            response = db_service.supabase.table('candidate_references')\
                .select('*')\
                .execute()

        return {
            "success": True,
            "count": len(response.data),
            "candidate_references": response.data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/reference-requests")
async def debug_reference_requests():
    """Debug endpoint to check reference_requests in database"""
    try:
        response = db_service.supabase.table('reference_requests')\
            .select('*')\
            .execute()

        return {
            "success": True,
            "count": len(response.data),
            "reference_requests": response.data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/workflow-test")
async def debug_workflow_test(resume_url: str, role: str, organization: str):
    """Test the workflow directly"""
    try:
        result = await workflow.run_workflow(
            resume_url=resume_url,
            role=role,
            organization=organization
        )
        
        # Validate the result
        validated_result = validate_extracted_data(result)
        
        return {
            "success": True, 
            "raw_result": result,
            "validated_result": validated_result
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/fix-extraction-flags")
async def debug_fix_extraction_flags():
    """One-time fix for existing applications"""
    try:
        # Get all applications
        response = db_service.supabase.table('applications')\
            .select('*')\
            .execute()
        
        fixed_count = 0
        for app in response.data:
            extracted_data = app.get('extracted_data', {})
            
            # Check if we actually have extracted data
            has_real_data = any([
                extracted_data.get('name'),
                extracted_data.get('email'), 
                extracted_data.get('phone'),
                extracted_data.get('references')
            ])
            
            if has_real_data and not app.get('has_extracted_data'):
                # Extract keys
                keys = []
                if extracted_data.get('name'):
                    keys.append('name')
                if extracted_data.get('email'):
                    keys.append('email')
                if extracted_data.get('phone'):
                    keys.append('phone')
                if extracted_data.get('references'):
                    keys.append('references')
                
                # Update the application
                db_service.supabase.table('applications')\
                    .update({
                        'has_extracted_data': True,
                        'extracted_data_keys': ','.join(keys) if keys else 'none'
                    })\
                    .eq('id', app['id'])\
                    .execute()
                
                fixed_count += 1
                print(f"✅ Fixed application {app['id']}")
        
        return {"success": True, "fixed_count": fixed_count}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/test-extraction/{application_id}")
async def debug_test_extraction(application_id: str):
    """Check what data was extracted for a specific application"""
    try:
        response = db_service.supabase.table('applications')\
            .select('*')\
            .eq('id', application_id)\
            .single()\
            .execute()
        
        app = response.data
        extracted_data = app.get('extracted_data', {})
        
        return {
            "application_id": application_id,
            "has_extracted_data": app.get('has_extracted_data'),
            "extracted_data_keys": app.get('extracted_data_keys'),
            "extracted_data": extracted_data,
            "has_real_data": any([
                extracted_data.get('name'),
                extracted_data.get('email'),
                extracted_data.get('phone'), 
                extracted_data.get('references')
            ])
        }
    except Exception as e:
        return {"error": str(e)}
=======
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
        
        # Update application in database
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
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Reference Checking System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)