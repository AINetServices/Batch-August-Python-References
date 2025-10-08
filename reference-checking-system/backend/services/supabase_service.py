"""
Supabase service for database operations.
"""

import os
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from datetime import datetime


class SupabaseService:
    """Service class for Supabase database operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        print(f"Supabase URL: {'Set' if self.supabase_url else 'Not set'}")
        print(f"Supabase Key: {'Set' if self.supabase_key else 'Not set'}")
        
        if not self.supabase_url or not self.supabase_key:
            print("Warning: Supabase credentials not found. Running in demo mode.")
            self.supabase = None
            self.demo_mode = True
        else:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                self.demo_mode = False
                print("Successfully connected to Supabase")
            except Exception as e:
                print(f"Error connecting to Supabase: {e}")
                print("Falling back to demo mode")
                self.supabase = None
                self.demo_mode = True

    def update_application(self, *args, **kwargs):
        """Universal update_application that handles ANY parameter pattern"""
        print(f"🚨 update_application CALLED - TRACING SOURCE")
        import traceback
        # Print the call stack to find where this is being called from
        for i, line in enumerate(traceback.format_stack()[:-1]):
            if 'supabase_service.py' not in line:
                print(f"   Caller {i}: {line.strip()}")
        
        print(f"📦 Raw call received:")
        print(f"   args: {args}")
        print(f"   kwargs: {kwargs}")
        
        # Extract parameters from ANY possible pattern
        application_id = None
        extracted_data = {}
        role = ""
        organization = ""
        user_id = None
        status = "extracted"
        
        # Try to extract from kwargs first
        if kwargs:
            application_id = (kwargs.get('application_id') or 
                             kwargs.get('p_application_id') or 
                             kwargs.get('app_id'))
            
            extracted_data = (kwargs.get('extracted_data') or 
                             kwargs.get('data') or 
                             kwargs.get('extracted_data') or {})
            
            role = (kwargs.get('role') or 
                   kwargs.get('p_role') or 
                   kwargs.get('role_name') or '')
            
            organization = (kwargs.get('organization') or 
                           kwargs.get('p_organization') or 
                           kwargs.get('org') or '')
            
            user_id = (kwargs.get('user_id') or 
                      kwargs.get('p_user_id') or 
                      kwargs.get('user'))
            
            status = (kwargs.get('status') or 
                     kwargs.get('p_status') or 
                     kwargs.get('state') or 'extracted')
        
        # If we didn't get what we need from kwargs, try args
        if not application_id and args:
            if len(args) > 0:
                application_id = args[0]
            if len(args) > 1:
                extracted_data = args[1] if isinstance(args[1], dict) else {}
            if len(args) > 2:
                role = args[2]
            if len(args) > 3:
                organization = args[3]
            if len(args) > 4:
                user_id = args[4]
            if len(args) > 5:
                status = args[5]
        
        print(f"🎯 Extracted parameters:")
        print(f"   application_id: {application_id}")
        print(f"   role: {role}")
        print(f"   organization: {organization}")
        print(f"   user_id: {user_id}")
        print(f"   status: {status}")
        print(f"   extracted_data: {type(extracted_data)}")
        
        if self.demo_mode:
            print(f"Demo mode: Would update application {application_id}")
            return {"success": True, "demo_mode": True, "message": "Demo mode - application would be updated"}
        
        if not application_id:
            return {"error": "application_id is required"}
        
        try:
            # Prepare update data
            update_data = {
                'role': role,
                'organization': organization,
                'extracted_data': extracted_data,
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            # Only add user_id if it's provided and not empty
            if user_id:
                update_data['user_id'] = user_id
            
            # Add resume_url if present in extracted_data
            if extracted_data and "resume_url" in extracted_data:
                update_data["resume_url"] = extracted_data["resume_url"]
            
            print(f"💾 Final update data:")
            for key, value in update_data.items():
                if key != 'extracted_data':
                    print(f"   {key}: {value}")
            
            response = self.supabase.table('applications').update(update_data).eq('id', application_id).execute()

            print(f"✅ Application {application_id} updated successfully")
            return {"success": True, "application_id": application_id, "data": response.data}
            
        except Exception as e:
            print(f"❌ Error updating application: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to update application: {str(e)}"}

   async def update_application_status(self, application_id: str, status: str, extracted_data: dict = None):
    """Update application status with optional extracted_data"""
    print(f"🔄 Updating application {application_id} status to {status}")
    
    if self.demo_mode:
        print(f"Demo mode: Would update application {application_id} status to {status}")
        return {"success": True, "demo_mode": True, "message": "Demo mode - status would be updated"}
    
    try:
        update_data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        
        # Add extracted_data if provided
        if extracted_data is not None:
            update_data['extracted_data'] = extracted_data
        
        print(f"💾 Update data being sent to database:")
        print(f"   Status: {status}")
        print(f"   Has extracted_data: {extracted_data is not None}")
        
        response = self.supabase.table('applications')\
            .update(update_data)\
            .eq('id', application_id)\
            .execute()

        print(f"✅ Application status updated to {status}")
        return {"success": True, "data": response.data}
    except Exception as e:
        print(f"❌ Error updating application status: {str(e)}")
        return {"error": f"Failed to update application status: {str(e)}"}
    def update_status(self, table: str, record_id: str, status: str) -> Dict[str, Any]:
        """Update status of a record"""
        if self.demo_mode:
            return {"success": True, "demo_mode": True, "message": "Demo mode - status would be updated"}
        
        try:
            response = self.supabase.table(table).update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', record_id).execute()

            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": f"Failed to update status: {str(e)}"}

    def create_application(
        self,
        user_id: str,
        role: str, 
        organization: str,
        resume_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new application record"""
        if self.demo_mode:
            print(f"Demo mode: Would create application for user {user_id}")
            return {
                "success": True, 
                "demo_mode": True, 
                "application_id": "demo-app-id-123",
                "message": "Demo mode - application would be created"
            }
        
        try:
            application_data = {
                'user_id': user_id,
                'role': role,
                'organization': organization,
                'status': 'uploaded',
                'resume_url': resume_url,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            response = self.supabase.table('applications').insert(application_data).execute()
            
            if response.data:
                application_id = response.data[0]['id']
                print(f"✅ Application created with ID: {application_id}")
                return {
                    "success": True, 
                    "application_id": application_id, 
                    "data": response.data
                }
            else:
                return {"error": "No data returned after creating application"}
                
        except Exception as e:
            print(f"❌ Error creating application: {str(e)}")
            return {"error": f"Failed to create application: {str(e)}"}

    async def create_candidate_reference(self, candidate_id: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a candidate reference"""
        print(f"🔄 Creating candidate reference for candidate_id: {candidate_id}")
        return self.create_reference(
            application_id=candidate_id,
            reference_data=reference_data,
            questions=[]
        )

    async def create_reference_requests(self, candidate_id: str, references: List) -> Dict[str, Any]:
        """Create reference requests in the database"""
        print(f"🔄 Creating reference requests for candidate_id: {candidate_id}")
        print(f"   Number of references: {len(references)}")
        
        if self.demo_mode:
            return {"success": True, "demo_mode": True}
        
        try:
            created_count = 0
            for ref in references:
                if isinstance(ref, dict):
                    name = ref.get('name', 'Unknown')
                    email = ref.get('email', '')
                else:
                    name = str(ref)[:50]
                    email = ""
                
                request_data = {
                    'candidate_id': candidate_id,
                    'reference_name': name,
                    'reference_email': email,
                    'status': 'pending',
                    'created_at': datetime.now().isoformat()
                }
                
                response = self.supabase.table('reference_requests').insert(request_data).execute()
                if response.data:
                    created_count += 1
            
            print(f"✅ Created {created_count} reference requests")
            return {"success": True, "created_count": created_count}
            
        except Exception as e:
            print(f"❌ Error creating reference requests: {str(e)}")
            return {"error": str(e)}

    async def get_application_by_user_and_role(self, user_id: str, role: str, organization: str) -> Dict[str, Any]:
        """Get application by user ID, role, and organization"""
        print(f"🔄 Getting application for user {user_id}, role {role}, org {organization}")
        
        if self.demo_mode:
            return {"success": True, "data": []}
        
        try:
            response = self.supabase.table('applications')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('role', role)\
                .eq('organization', organization)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()

            return {"success": True, "data": response.data}
        except Exception as e:
            print(f"❌ Error getting application: {str(e)}")
            return {"error": str(e)}