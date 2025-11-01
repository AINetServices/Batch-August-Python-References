"""
Service for interacting with Supabase database and storage.
"""

import os
import json
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    """Service class for Supabase operations"""
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("VITE_SUPABASE_URL"),
            os.getenv("VITE_SUPABASE_SERVICE_KEY")
        )

    async def update_application(self, user_id: str, role: str, organization: str, 
                               extracted_data: Dict[str, Any], status: str = "extracted") -> Dict[str, Any]:
        """Update application with extracted data"""
        try:
            # Find the application
            response = self.supabase.table('applications')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('role', role)\
                .eq('organization', organization)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if not response.data:
                return {"error": "Application not found"}
            
            application_id = response.data[0]['id']
            
            # Update the application
            update_response = self.supabase.table('applications').update({
                'extracted_data': extracted_data,
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', application_id).execute()
            
            return {"success": True, "application_id": application_id, "data": update_response.data}
            
        except Exception as e:
            return {"error": f"Failed to update application: {str(e)}"}

    async def create_reference(self, application_id: str, reference_data: Dict[str, Any], 
                             questions: List[str]) -> Dict[str, Any]:
        """Create a reference record"""
        try:
            reference_record = {
                'application_id': application_id,
                'name': reference_data.get('name', ''),
                'email': reference_data.get('email', ''),
                'company': reference_data.get('company', ''),
                'relationship': reference_data.get('relationship', ''),
                'years_worked': reference_data.get('years_worked', ''),
                'questions_sent': questions,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('references').insert(reference_record).execute()
            return {"success": True, "data": response.data}
            
        except Exception as e:
            return {"error": f"Failed to create reference: {str(e)}"}

    async def update_application_status(self, application_id: str, status: str) -> Dict[str, Any]:
        """Update application status"""
        try:
            response = self.supabase.table('applications').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', application_id).execute()
            
            return {"success": True, "data": response.data}
            
        except Exception as e:
            return {"error": f"Failed to update status: {str(e)}"}

    async def get_questions(self, role: str, organization: str) -> List[str]:
        """Get predefined questions for a role and organization"""
        try:
            response = self.supabase.table('questions')\
                .select('questions')\
                .eq('role', role)\
                .eq('organization', organization)\
                .execute()
            
            if response.data:
                questions_data = response.data[0]['questions']
                if isinstance(questions_data, list):
                    return questions_data
                elif isinstance(questions_data, str):
                    return json.loads(questions_data)
            
            return []
            
        except Exception as e:
            print(f"Error fetching questions: {str(e)}")
            return []

    async def upload_file(self, bucket: str, file_path: str, file_content: bytes) -> Dict[str, Any]:
        """Upload file to Supabase storage"""
        try:
            response = self.supabase.storage.from_(bucket).upload(file_path, file_content)
            
            if response.get('error'):
                return {"error": response['error']['message']}
            
            # Get public URL
            public_url = self.supabase.storage.from_(bucket).get_public_url(file_path)
            
            return {"success": True, "url": public_url}
            
        except Exception as e:
            return {"error": f"Failed to upload file: {str(e)}"}

    async def get_application_details(self, application_id: str) -> Dict[str, Any]:
        """Get detailed application information including references"""
        try:
            # Get application
            app_response = self.supabase.table('applications')\
                .select('*')\
                .eq('id', application_id)\
                .execute()
            
            if not app_response.data:
                return {"error": "Application not found"}
            
            application = app_response.data[0]
            
            # Get references
            ref_response = self.supabase.table('references')\
                .select('*')\
                .eq('application_id', application_id)\
                .execute()
            
            application['references'] = ref_response.data or []
            
            return {"success": True, "data": application}
            
        except Exception as e:
            return {"error": f"Failed to get application details: {str(e)}"}

    async def update_reference_response(self, reference_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Update reference with responses"""
        try:
            response = self.supabase.table('references').update({
                'responses': responses,
                'status': 'responded'
            }).eq('id', reference_id).execute()
            
            return {"success": True, "data": response.data}
            
        except Exception as e:
            return {"error": f"Failed to update reference response: {str(e)}"}