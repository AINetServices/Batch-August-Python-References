"""
Multi-agent workflow using LangGraph for processing resumes and extracting references.
Implements a comprehensive pipeline with custom tools and state management.
"""

import os
import json
from typing import Dict, List, Any, TypedDict
from datetime import datetime
import requests
from io import BytesIO

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.agents import AgentExecutor

from .tools.resume_tools import ResumeParserTool, ReferenceExtractorTool
from .tools.database_tools import QuestionFetcherTool
from .tools.vector_tools import VectorStoreTool

class WorkflowState(TypedDict):
    """State structure for the multi-agent workflow"""
    resume_url: str
    role: str
    organization: str
    resume_text: str
    applicant_info: Dict[str, Any]
    references: List[Dict[str, Any]]
    questions: List[str]
    vectorstore_path: str
    error_message: str
    status: str

class ReferenceCheckingWorkflow:
    """
    Multi-agent workflow orchestrator using LangGraph.
    Manages the complete pipeline from resume processing to reference extraction.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY")
        )
        print(os.getenv("GROQ_API_KEY"))
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
        
        # Initialize tools
        self.resume_parser = ResumeParserTool(llm=self.llm)
        self.reference_extractor = ReferenceExtractorTool(llm=self.llm)
        self.question_fetcher = QuestionFetcherTool()
        self.vector_tool = VectorStoreTool(embeddings=self.embeddings)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the multi-agent workflow using LangGraph"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("download_resume", self._download_resume_node)
        workflow.add_node("parse_resume", self._parse_resume_node)
        workflow.add_node("extract_applicant", self._extract_applicant_node)
        workflow.add_node("extract_references", self._extract_references_node)
        workflow.add_node("build_vectorstore", self._build_vectorstore_node)
        workflow.add_node("fetch_questions", self._fetch_questions_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Add edges to define the flow
        workflow.add_edge("download_resume", "parse_resume")
        workflow.add_edge("parse_resume", "extract_applicant")
        workflow.add_edge("extract_applicant", "extract_references")
        workflow.add_edge("extract_references", "build_vectorstore")
        workflow.add_edge("build_vectorstore", "fetch_questions")
        workflow.add_edge("fetch_questions", "finalize")
        workflow.add_edge("finalize", END)
        
        # Set entry point
        workflow.set_entry_point("download_resume")
        
        return workflow.compile()

    async def _download_resume_node(self, state: WorkflowState) -> WorkflowState:
        """Download and extract text from resume URL"""
        try:
            response = requests.get(state["resume_url"])
            response.raise_for_status() 
            
            # Use resume parser to extract text
            resume_text = self.resume_parser.parse_file_content(
                BytesIO(response.content), 
                state["resume_url"] 
            )
            
            state["resume_text"] = resume_text
            state["status"] = "downloaded"
            
        except Exception as e:
            state["error_message"] = f"Failed to download resume: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _parse_resume_node(self, state: WorkflowState) -> WorkflowState:
        """Parse resume text into structured chunks"""
        try:
            if state["status"] == "error":
                return state
                
            # Split text into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " "]
            )
            
            chunks = text_splitter.split_text(state["resume_text"])
            state["resume_chunks"] = chunks
            state["status"] = "parsed"
            
        except Exception as e:
            state["error_message"] = f"Failed to parse resume: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _extract_applicant_node(self, state: WorkflowState) -> WorkflowState:
        """Extract applicant information using LLM agent"""
        try:
            if state["status"] == "error":
                return state
                
            # Create specialized agent for applicant extraction
            applicant_agent = self._create_applicant_agent()
            

            result = applicant_agent.invoke({
                "messages": [
                    {"role": "user", "content": f"Extract applicant info from this resume: {state['resume_text']}"}
                ]
            })
            
            # Parse the result
            from langchain_core.messages import ToolMessage
            tool_content = next((msg.content for msg in result["messages"] if isinstance(msg, ToolMessage) and msg.name == "extract_applicant_info"), None)
            applicant_info = self._parse_applicant_info(tool_content)
            state["applicant_info"] = applicant_info
            state["status"] = "applicant_extracted"
            
        except Exception as e:
            state["error_message"] = f"Failed to extract applicant info: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _extract_references_node(self, state: WorkflowState) -> WorkflowState:
        """Extract reference information using specialized agent"""
        try:
            if state["status"] == "error":
                return state
                
            # Create specialized agent for reference extraction
            reference_agent = self._create_reference_agent()
            
            # Extract references # you need to fix everywhere where it invokes like this with input, resume text to the applicant node one
            result = reference_agent.invoke({
                "input": f"Extract reference contacts from this resume for {state['role']} position",
                "resume_text": state["resume_text"],
                "role": state["role"]
            })
            
            # Parse references
            references = self._parse_references(result["output"])
            state["references"] = references
            state["status"] = "references_extracted"
            
        except Exception as e:
            state["error_message"] = f"Failed to extract references: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _build_vectorstore_node(self, state: WorkflowState) -> WorkflowState:
        """Build vector store for semantic search"""
        try:
            if state["status"] == "error":
                return state
                
            # Create documents from resume chunks
            documents = [Document(page_content=chunk) for chunk in state.get("resume_chunks", [])]
            
            # Build vector store
            vectorstore_path = f"./vectorstore/{state['role']}_{state['organization']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if documents:
                vectorstore = Chroma.from_documents(
                    documents,
                    self.embeddings,
                    persist_directory=vectorstore_path
                )
                vectorstore.persist()
                
            state["vectorstore_path"] = vectorstore_path
            state["status"] = "vectorstore_built"
            
        except Exception as e:
            state["error_message"] = f"Failed to build vectorstore: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _fetch_questions_node(self, state: WorkflowState) -> WorkflowState:
        """Fetch predefined questions for the role and organization"""
        try:
            if state["status"] == "error":
                return state
                
            # Fetch questions from database
            questions = await self.question_fetcher.get_questions(
                state["role"], 
                state["organization"]
            )
            
            state["questions"] = questions
            state["status"] = "questions_fetched"
            
        except Exception as e:
            state["error_message"] = f"Failed to fetch questions: {str(e)}"
            state["status"] = "error"
            
        return state

    async def _finalize_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow and prepare results"""
        try:
            if state["status"] == "error":
                return state
                
            state["status"] = "completed"
            
        except Exception as e:
            state["error_message"] = f"Failed to finalize: {str(e)}"
            state["status"] = "error"
            
        return state

    def _create_applicant_agent(self) -> AgentExecutor:
        """Create specialized agent for extracting applicant information"""
        
        @tool
        def extract_applicant_info(resume_text: str) -> str:
            """Extract applicant name, contact info, and basic details from resume"""
            prompt = PromptTemplate.from_template("""
            Extract the following applicant information from this resume text:
            
            Resume Text:
            {resume_text}
            
            Extract and return as JSON in the following format:
            - full_name: The applicant's full name
            - email: Email address
            - phone: Phone number
            - current_position: Current job title/position
            - experience_years: Estimated years of experience
            - key_skills: List of main skills/competencies
            
            Return only the JSON object and nothing else, no code no other information, only pure JSON:
            """)
            
            result = self.llm.invoke(prompt.format(resume_text=resume_text))
            return result.content
        
        tools = [extract_applicant_info]
        return create_react_agent(self.llm, tools)

    def _create_reference_agent(self) -> AgentExecutor:
        """Create specialized agent for extracting reference information"""
        
        @tool
        def extract_references(resume_text: str, role: str) -> str:
            """Extract reference contacts from resume text"""
            prompt = PromptTemplate.from_template("""
            Extract reference information from this resume for a {role} position:
            
            Resume Text:
            {resume_text}
            
            Look for:
            - Previous supervisors, managers, or colleagues
            - Contact information (email, phone)
            - Company/organization names
            - Working relationship and duration
            
            Return as JSON array with objects containing:
            - name: Reference's full name
            - email: Email address (if available)
            - company: Company/organization
            - relationship: Professional relationship (e.g., "Direct supervisor", "Colleague")
            - years_worked: Duration worked together
            - context: Brief context of their working relationship
            
            Return only the JSON array:
            """)
            
            result = self.llm.invoke(prompt.format(resume_text=resume_text, role=role))
            return result.content
        
        tools = [extract_references]
        return create_react_agent(self.llm, tools)

    def _parse_applicant_info(self, llm_output: str) -> Dict[str, Any]:
        """Parse LLM output into structured applicant information"""
        try:
            # Try to extract JSON from the output
            start_idx = llm_output.find('{')
            end_idx = llm_output.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = llm_output[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create basic structure
                return {
                    "full_name": "Unknown",
                    "email": "Unknown",
                    "phone": "Unknown",
                    "current_position": "Unknown",
                    "experience_years": "Unknown",
                    "key_skills": []
                }
        except json.JSONDecodeError:
            return {"error": "Failed to parse applicant information"}

    def _parse_references(self, llm_output: str) -> List[Dict[str, Any]]:
        """Parse LLM output into structured reference information"""
        try:
            # Try to extract JSON from the output
            start_idx = llm_output.find('[')
            end_idx = llm_output.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = llm_output[start_idx:end_idx]
                references = json.loads(json_str)
                
                # Validate and clean references
                cleaned_refs = []
                for ref in references:
                    if isinstance(ref, dict) and ref.get("name"):
                        cleaned_refs.append({
                            "name": ref.get("name", "Unknown"),
                            "email": ref.get("email", "Not provided"),
                            "company": ref.get("company", "Unknown"),
                            "relationship": ref.get("relationship", "Professional contact"),
                            "years_worked": ref.get("years_worked", "Unknown"),
                            "context": ref.get("context", "")
                        })
                
                return cleaned_refs
            else:
                return []
        except json.JSONDecodeError:
            return []

    async def run_workflow(self, resume_url: str, role: str, organization: str) -> Dict[str, Any]:
        """
        Run the complete multi-agent workflow
        """
        initial_state = WorkflowState(
            resume_url=resume_url,
            role=role,
            organization=organization,
            resume_text="",
            applicant_info={},
            references=[],
            questions=[],
            vectorstore_path="",
            error_message="",
            status="initialized"
        )
        
        # Execute the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Return the results
        return {
            "applicant_info": final_state.get("applicant_info", {}),
            "references": final_state.get("references", []),
            "questions": final_state.get("questions", []),
            "vectorstore_path": final_state.get("vectorstore_path", ""),
            "status": final_state.get("status", "unknown"),
            "error_message": final_state.get("error_message", "")
        }