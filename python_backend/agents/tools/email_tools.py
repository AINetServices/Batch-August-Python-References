# Add this import at the top
from .tools.email_tools import create_reference_emailer_tool

class ReferenceCheckingWorkflow:
    def __init__(self):
        # ... existing init code ...
        
        # Initialize email tool
        self.email_tool = create_reference_emailer_tool()
        
        # ... rest of init ...

    # ADD THIS NEW NODE METHOD
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

    # UPDATE the _build_workflow method to include email node
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)
        
        # Add all existing nodes
        workflow.add_node("download_resume", self._download_resume_node)
        workflow.add_node("parse_resume", self._parse_resume_node)
        workflow.add_node("extract_applicant", self._extract_applicant_node)
        workflow.add_node("extract_references", self._extract_references_node)
        workflow.add_node("build_vectorstore", self._build_vectorstore_node)
        workflow.add_node("fetch_questions", self._fetch_questions_node)
        
        # ADD THE EMAIL NODE
        workflow.add_node("send_emails", self._send_emails_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Update edges to include email node
        workflow.add_edge("fetch_questions", "send_emails")  # Changed this
        workflow.add_edge("send_emails", "finalize")         # Added this
        workflow.add_edge("finalize", END)
        
        workflow.set_entry_point("download_resume")
        return workflow.compile()

    # REPLACE the dummy run_workflow with the real one
    async def run_workflow(self, resume_url: str, role: str, organization: str) -> Dict[str, Any]:
    """
    Run the complete multi-agent workflow - TEMPORARY DEBUG VERSION
    """
    print(f"🎯 DEBUG: Workflow started for {role} at {organization}")
    
    # TEMPORARY: Return dummy data to test the flow
    dummy_result = {
        "applicant_info": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "current_position": "Registered Nurse",
            "experience_years": "5",
            "key_skills": ["Patient Care", "Emergency Response", "Medical Documentation"]
        },
        "references": [
            {
                "name": "Dr. Sarah Smith",
                "email": "sarah.smith@hospital.com",
                "company": "City General Hospital",
                "relationship": "Supervisor",
                "years_worked": "3",
                "context": "Direct supervisor in cardiology department"
            },
            {
                "name": "Mike Johnson",
                "email": "mike.johnson@clinic.com", 
                "company": "Community Health Clinic",
                "relationship": "Colleague",
                "years_worked": "2",
                "context": "Worked together in emergency room"
            }
        ],
        "questions": [
            "How would you rate the candidate's clinical skills?",
            "Can you describe their patient care approach?",
            "How do they handle emergency situations?"
        ],
        "vectorstore_path": "",  # ← ADD THIS LINE
        "email_results": {},     # ← ADD THIS LINE
        "status": "completed",
        "error_message": ""
    }
    
    print(f"✅ DEBUG: Returning dummy data")
    return dummy_result