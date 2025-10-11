"""
Custom tools for interacting with Supabase database.
"""

import os
import json
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
from supabase import create_client, Client
from pydantic import BaseModel

class QuestionFetcherTool(BaseTool):
    """Tool for fetching predefined questions from Supabase database"""
    
    name: str = "question_fetcher"
    description: str = "Fetch predefined reference questions based on role and organization"
    supabase: Client
    # def __init__(self):
    #     super().__init__()
    #     self.supabase: Client = create_client(
    #         os.getenv("VITE_SUPABASE_URL"),
    #         os.getenv("VITE_SUPABASE_ANON_KEY")
    #     )
    def __init__(self):
            # Simple and clear - create client, pass to parent
            supabase_client = create_client(
                os.getenv("VITE_SUPABASE_URL"),
                os.getenv("VITE_SUPABASE_ANON_KEY")
            )
            super().__init__(supabase=supabase_client)

    def _run(self, role: str, organization: str) -> List[str]:
        """Fetch questions for a specific role and organization"""
        try:
            response = self.supabase.table('questions').select('questions').eq('role', role).eq('organization', organization).execute()
            
            if response.data:
                questions_data = response.data[0]['questions']
                if isinstance(questions_data, list):
                    return questions_data
                elif isinstance(questions_data, str):
                    return json.loads(questions_data)
            
            # Fallback to generic questions if specific ones not found
            return self._get_generic_questions(role)
            
        except Exception as e:
            return [f"Error fetching questions: {str(e)}"]

    def _get_generic_questions(self, role: str) -> List[str]:
        """Return generic questions based on role category"""
        generic_questions = {
            "software": [
                "How would you rate the candidate's technical skills and problem-solving abilities?",
                "Can you describe a challenging project they worked on and how they approached it?",
                "How did they collaborate with team members and handle code reviews?",
                "What are their strongest programming languages and technical competencies?",
                "Would you recommend them for a senior software development position?"
            ],
            "marketing": [
                "How would you evaluate their campaign management and strategic thinking?",
                "Can you provide examples of successful marketing initiatives they led?",
                "How did they handle budget management and performance metrics?",
                "What are their strengths in team leadership and client relations?",
                "Would you hire them again for a marketing leadership role?"
            ],
            "management": [
                "How would you assess their leadership and team management skills?",
                "Can you describe how they handled difficult situations or conflicts?",
                "How did they contribute to achieving team and organizational goals?",
                "What are their strengths in communication and decision-making?",
                "Would you recommend them for a senior management position?"
            ],
            "default": [
                "How would you describe the candidate's work performance and professionalism?",
                "What are their key strengths and areas of expertise?",
                "How did they handle challenges and work under pressure?",
                "Can you provide examples of their contributions to team success?",
                "Would you recommend them for a position in their field of expertise?"
            ]
        }
        
        role_lower = role.lower()
        
        if any(tech_term in role_lower for tech_term in ["software", "developer", "engineer", "programmer"]):
            return generic_questions["software"]
        elif any(marketing_term in role_lower for marketing_term in ["marketing", "brand", "campaign", "digital"]):
            return generic_questions["marketing"]
        elif any(mgmt_term in role_lower for mgmt_term in ["manager", "director", "lead", "supervisor"]):
            return generic_questions["management"]
        else:
            return generic_questions["default"]

    async def get_questions(self, role: str, organization: str) -> List[str]:
        """Async wrapper for getting questions"""
        return self._run(role, organization)

    async def _arun(self, role: str, organization: str) -> List[str]:
        """Async version of _run"""
        return self._run(role, organization)


class DatabaseUpdateTool(BaseTool):
    """Tool for updating application and reference data in Supabase"""
    
    name: str = "database_updater"
    description: str = "Update application status and reference information in the database"
    
    def __init__(self):
        super().__init__()
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Perform database operations based on action type"""
        try:
            if action == "update_application":
                return self._update_application(**kwargs)
            elif action == "create_references":
                return self._create_references(**kwargs)
            elif action == "update_status":
                return self._update_status(**kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Database operation failed: {str(e)}"}

    def _update_application(self, application_id: str, extracted_data: Dict, status: str = "extracted") -> Dict[str, Any]:
        """Update application with extracted data"""
        try:
            response = self.supabase.table('applications').update({
                'extracted_data': extracted_data,
                'status': status,
                'updated_at': 'now()'
            }).eq('id', application_id).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": f"Failed to update application: {str(e)}"}

    def _create_references(self, application_id: str, references: List[Dict]) -> Dict[str, Any]:
        """Create reference records for an application"""
        try:
            reference_records = []
            for ref in references:
                reference_records.append({
                    'application_id': application_id,
                    'name': ref.get('name', ''),
                    'email': ref.get('email', ''),
                    'company': ref.get('company', ''),
                    'relationship': ref.get('relationship', ''),
                    'years_worked': ref.get('years_worked', ''),
                    'status': 'pending'
                })
            
            response = self.supabase.table('references').insert(reference_records).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": f"Failed to create references: {str(e)}"}

    def _update_status(self, table: str, record_id: str, status: str) -> Dict[str, Any]:
        """Update status of a record"""
        try:
            response = self.supabase.table(table).update({
                'status': status,
                'updated_at': 'now()'
            }).eq('id', record_id).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": f"Failed to update status: {str(e)}"}

    async def _arun(self, action: str, **kwargs) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(action, **kwargs)