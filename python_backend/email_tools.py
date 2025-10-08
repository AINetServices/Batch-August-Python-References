"""
Email tools for sending reference check questions to references.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv
s
load_dotenv()

class ReferenceEmailer:
    """Tool for sending reference check emails"""
    
    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
    
    def send_reference_check_email(
        self, 
        reference: Dict[str, Any], 
        applicant_name: str,
        role: str,
        organization: str,
        questions: List[str]
    ) -> bool:
        """
        Send reference check questions to a reference contact.
        """
        if not self.email_user or not self.email_password:
            print("❌ Email credentials not configured")
            return False
        
        reference_name = reference.get('name', 'Reference')
        reference_email = reference.get('email', '')
        
        if not reference_email:
            print(f"❌ No email address for reference: {reference_name}")
            return False
        
        # Create email subject
        subject = f"Reference Check Request for {applicant_name} - {organization}"
        
        # Create email body
        body = self._create_email_body(
            reference_name=reference_name,
            applicant_name=applicant_name,
            role=role,
            organization=organization,
            questions=questions
        )
        
        # Send email
        return self._send_email(subject, body, reference_email)
    
    def _create_email_body(
        self,
        reference_name: str,
        applicant_name: str,
        role: str,
        organization: str,
        questions: List[str]
    ) -> str:
        """Create the email body with questions"""
        
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        return f"""
Dear {reference_name},

I hope this message finds you well. We are conducting reference checks for {applicant_name} who has applied for the {role} position at {organization}.

{applicant_name} listed you as a reference, and we would greatly appreciate your insights about their qualifications and work experience.

Could you please provide your feedback on the following questions:

{questions_text}

Please feel free to share any additional comments or observations that you believe would be helpful in our evaluation.

Thank you for your time and assistance.

Best regards,
{organization} Hiring Team
"""
    
    def _send_email(self, subject: str, body: str, to_email: str) -> bool:
        """Send email using SMTP"""
        try:
            from email.message import EmailMessage
            import smtplib
            
            msg = EmailMessage()
            msg.set_content(body.strip())
            msg["Subject"] = subject
            msg["From"] = self.email_user
            msg["To"] = to_email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False

# Simple function-based tool for LangChain
def create_reference_emailer_tool():
    """Create a reference emailer tool for LangChain"""
    emailer = ReferenceEmailer()
    
    def send_reference_emails(
        references: List[Dict[str, Any]],
        applicant_info: Dict[str, Any],
        role: str, 
        organization: str,
        questions: List[str]
    ) -> Dict[str, Any]:
        """
        Send reference check emails to all references.
        """
        results = {
            "sent": [],
            "failed": [],
            "total_attempted": 0,
            "total_successful": 0
        }
        
        applicant_name = applicant_info.get('full_name', 'The applicant')
        
        for reference in references:
            reference_name = reference.get('name', 'Unknown')
            reference_email = reference.get('email', '')
            
            if not reference_email:
                print(f"⚠️ Skipping {reference_name} - no email address")
                results["failed"].append({
                    "name": reference_name,
                    "reason": "No email address"
                })
                continue
            
            results["total_attempted"] += 1
            
            success = emailer.send_reference_check_email(
                reference=reference,
                applicant_name=applicant_name,
                role=role,
                organization=organization,
                questions=questions
            )
            
            if success:
                results["sent"].append({
                    "name": reference_name,
                    "email": reference_email
                })
                results["total_successful"] += 1
            else:
                results["failed"].append({
                    "name": reference_name,
                    "email": reference_email,
                    "reason": "Email sending failed"
                })
        
        return results
    
    return send_reference_emails