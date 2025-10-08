"""
Custom tools for interacting with Supabase database.
"""

import os
import json
from typing import Any, Dict, List, Optional
from supabase import create_client, Client


# Create simple function-based tools
def create_question_fetcher_tool():
    """Create a question fetcher tool"""
    
    def fetch_questions(role: str, organization: str) -> List[str]:
        """Fetch questions for a specific role and organization"""
        try:
            supabase = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_SERVICE_KEY")
            )
            
            response = supabase.table('questions').select('questions').eq('role', role).eq('organization', organization).execute()

            if response.data:
                questions_data = response.data[0]['questions']
                if isinstance(questions_data, list):
                    return questions_data
                elif isinstance(questions_data, str):
                    return json.loads(questions_data)

            # Fallback to generic questions if specific ones not found   
            return _get_generic_questions(role)

        except Exception as e:
            return [f"Error fetching questions: {str(e)}"]
    
    return fetch_questions


def create_database_updater_tool():
    """Create a database updater tool"""
    
    def update_database(action: str, **kwargs) -> Dict[str, Any]:
        """Perform database operations based on action type"""
        try:
            supabase = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_SERVICE_KEY")
            )
            
            if action == "update_application":
                return _update_application(supabase, **kwargs)
            elif action == "create_references":
                return _create_references(supabase, **kwargs)
            elif action == "update_status":
                return _update_status(supabase, **kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Database operation failed: {str(e)}"}
    
    return update_database


# Helper functions
def _get_generic_questions(role: str) -> List[str]:
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


def _update_application(supabase: Client, application_id: str, extracted_data: Dict, status: str = "extracted") -> Dict[str, Any]:
    """Update application with extracted data"""
    try:
        response = supabase.table('applications').update({      
            'extracted_data': extracted_data,
            'status': status,
            'updated_at': 'now()'
        }).eq('id', application_id).execute()

        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": f"Failed to update application: {str(e)}"}


def _create_references(supabase: Client, application_id: str, references: List[Dict]) -> Dict[str, Any]:
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

        response = supabase.table('references').insert(reference_records).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": f"Failed to create references: {str(e)}"}


def _update_status(supabase: Client, table: str, record_id: str, status: str) -> Dict[str, Any]:
    """Update status of a record"""
    try:
        response = supabase.table(table).update({
            'status': status,
            'updated_at': 'now()'
        }).eq('id', record_id).execute()

        return {"success": True, "data": response.data}
    except Exception as e:
        return {"error": f"Failed to update status: {str(e)}"}


# Simple wrapper classes
class QuestionFetcherTool:
    def __init__(self):
        self._fetch_func = create_question_fetcher_tool()
    
    def _run(self, role: str, organization: str) -> List[str]:
        return self._fetch_func(role, organization)


class DatabaseUpdateTool:
    def __init__(self):
        self._update_func = create_database_updater_tool()
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        return self._update_func(action, **kwargs)
