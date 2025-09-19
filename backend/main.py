#!/usr/bin/env python3
import os
import sys
import getpass
from typing import Dict, Any
from dotenv import load_dotenv

from auth import AuthManager
from db import DatabaseManager
from graph import ReferenceWorkflow

load_dotenv()

def create_sample_data():
    """Create sample data for testing"""
    db = DatabaseManager()
    
    # Sample role and organization IDs (in real app, these would be proper UUIDs)
    sample_role_id = "550e8400-e29b-41d4-a716-446655440001"
    sample_org_id = "550e8400-e29b-41d4-a716-446655440002"
    
    print("Creating sample questions...")
    
    # Create sample questions
    sample_questions = [
        {
            "role_id": sample_role_id,
            "organization_id": sample_org_id,
            "text": "How would you rate the candidate's technical skills?",
            "category": "technical"
        },
        {
            "role_id": sample_role_id,
            "organization_id": sample_org_id,
            "text": "How would you describe their communication abilities?",
            "category": "communication"
        },
        {
            "role_id": sample_role_id,
            "organization_id": sample_org_id,
            "text": "Would you hire this candidate again?",
            "category": "overall"
        }
    ]
    
    try:
        for question in sample_questions:
            db.supabase.table("questions").insert(question).execute()
        print(f"✅ Created {len(sample_questions)} sample questions")
    except Exception as e:
        print(f"ℹ️ Sample questions might already exist: {e}")

def create_sample_resume():
    """Create a sample resume file for testing"""
    sample_content = """
John Doe
Senior Software Engineer

Experience:
- Senior Developer at TechCorp (2020-2023)
- Software Engineer at StartupInc (2018-2020)

References:
1. Jane Smith
   Email: jane.smith@techcorp.com
   Company: TechCorp
   Relationship: Direct Manager (2020-2023)

2. Bob Johnson  
   Email: bob.j@startupinc.com
   Company: StartupInc
   Relationship: Team Lead (2018-2020)

3. Sarah Wilson
   Email: s.wilson@consulting.com
   Company: Wilson Consulting
   Relationship: Project Collaborator (2019)
"""
    
    os.makedirs("/tmp", exist_ok=True)
    with open("/tmp/sample_resume.txt", "w") as f:
        f.write(sample_content)
    
    print("✅ Created sample resume at /tmp/sample_resume.txt")
    return "/tmp/sample_resume.txt"

def demo_signin():
    """Interactive sign-in demo"""
    auth = AuthManager()
    
    print("\n=== Authentication Demo ===")
    print("1. Sign In")
    print("2. Sign Up")
    print("3. Skip (for demo)")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ")
        
        result = auth.sign_in(email, password)
        if result["success"]:
            print(f"✅ Signed in successfully as {email}")
            return result["user"]["id"]
        else:
            print(f"❌ Sign in failed: {result['message']}")
            return None
    
    elif choice == "2":
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ")
        full_name = input("Full Name: ").strip()
        
        result = auth.sign_up(email, password, full_name)
        if result["success"]:
            print(f"✅ Signed up successfully as {email}")
            return result["user"]["id"]
        else:
            print(f"❌ Sign up failed: {result['message']}")
            return None
    
    else:
        # For demo purposes, create a mock user session
        print("ℹ️ Using demo mode (skipping authentication)")
        # In real implementation, this would not be allowed
        return "demo-user-id"

def run_workflow_demo():
    """Run the complete workflow demo"""
    print("\n🚀 Reference Application Workflow Demo")
    print("=" * 50)
    
    # Setup sample data
    create_sample_data()
    resume_file = create_sample_resume()
    
    # Authentication demo
    user_id = demo_signin()
    if not user_id:
        print("❌ Authentication required to proceed")
        return
    
    # Initialize workflow
    workflow = ReferenceWorkflow()
    
    # Prepare inputs
    inputs = {
        "user_id": user_id,
        "file_path": resume_file,
        "role_id": "550e8400-e29b-41d4-a716-446655440001",  # Sample role ID
        "organization_id": "550e8400-e29b-41d4-a716-446655440002"  # Sample org ID
    }
    
    print("\n🔄 Running workflow...")
    
    # Run workflow
    result = workflow.run_workflow(inputs)
    
    print("\n📊 Workflow Results:")
    print(f"User ID: {result.get('user_id')}")
    print(f"Application ID: {result.get('application_id')}")
    print(f"Resume Path: {result.get('resume_path')}")
    print(f"Parsed Data: {result.get('parsed')}")
    print(f"Questions Count: {len(result.get('questions', []))}")
    print(f"Approval Status: {result.get('approval_status')}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    
    return result

def approve_review(application_id: str):
    """Admin function to approve a question review"""
    db = DatabaseManager()
    
    print(f"\n🔍 Looking for question review for application: {application_id}")
    
    review = db.get_question_review(application_id)
    if not review:
        print("❌ Question review not found")
        return
    
    if review["status"] == "approved":
        print("ℹ️ Review is already approved")
        return
    
    print(f"📋 Review Status: {review['status']}")
    print(f"📋 Questions: {len(review.get('questions', []))}")
    
    confirm = input("Approve this review? (y/n): ").strip().lower()
    if confirm == 'y':
        result = db.approve_question_review(review["id"], "admin-user")
        if result["success"]:
            print("✅ Review approved successfully!")
            
            # Continue workflow if possible
            print("\n🔄 Continuing workflow...")
            workflow = ReferenceWorkflow()
            
            # Get application details
            app = db.get_application(application_id)
            if app:
                inputs = {
                    "user_id": app["applicant_id"],
                    "application_id": application_id,
                    "role_id": app["role_id"],
                    "organization_id": app["organization_id"],
                    "approval_status": "approved"
                }
                
                # Run only the remaining nodes
                result = workflow.send_reference_requests_node(inputs)
                if not result.get("error"):
                    print("✅ Reference requests sent successfully!")
                else:
                    print(f"❌ Failed to send reference requests: {result['error']}")
        else:
            print(f"❌ Failed to approve review: {result['error']}")
    else:
        print("❌ Review not approved")

def list_pending_reviews():
    """List all pending question reviews"""
    db = DatabaseManager()
    
    try:
        response = db.supabase.table("question_reviews").select("""
            *,
            applications:application_id (
                applicant_id,
                status
            )
        """).eq("status", "pending").execute()
        
        reviews = response.data or []
        
        print(f"\n📋 Found {len(reviews)} pending reviews:")
        for review in reviews:
            print(f"  - Application ID: {review['application_id']}")
            print(f"    Review ID: {review['id']}")
            print(f"    Questions: {len(review.get('questions', []))}")
            print(f"    Created: {review['created_at']}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing reviews: {e}")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Reference Application Workflow System")
        print("\nUsage:")
        print("  python main.py demo          - Run complete workflow demo")
        print("  python main.py approve <id>  - Approve question review")
        print("  python main.py list          - List pending reviews")
        print("  python main.py auth          - Test authentication only")
        return
    
    command = sys.argv[1].lower()
    
    if command == "demo":
        run_workflow_demo()
    
    elif command == "approve":
        if len(sys.argv) < 3:
            print("❌ Please provide application ID")
            print("Usage: python main.py approve <application_id>")
            return
        application_id = sys.argv[2]
        approve_review(application_id)
    
    elif command == "list":
        list_pending_reviews()
    
    elif command == "auth":
        demo_signin()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: demo, approve, list, auth")

if __name__ == "__main__":
    main()