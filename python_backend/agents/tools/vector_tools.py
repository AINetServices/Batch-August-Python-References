"""
<<<<<<< HEAD
Custom tools for vector store operations.
=======
Custom tools for vector store operations and semantic search.
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517
"""

import os
import json
<<<<<<< HEAD
from typing import Any, Dict, List, Optional, Type
from langchain.tools import BaseTool
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from supabase import create_client, Client
from pydantic import BaseModel, Field


# Define input schemas for each tool
class VectorSearchInput(BaseModel):
    query: str = Field(description="The search query")
    k: int = Field(default=3, description="Number of results to return")


class VectorStoreInput(BaseModel):
    action: str = Field(description="The vector store action to perform")
    kwargs: Dict[str, Any] = Field(default={}, description="Additional parameters for the action")


# Vector store tool with proper Pydantic annotations
class VectorStoreTool(BaseTool):
    name: str = Field(default="vector_store", description="The name of the tool")
    description: str = Field(
        default="Performs vector store operations like search and store",
        description="Description of what the tool does"
    )
    args_schema: Type[BaseModel] = VectorStoreInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._vector_func = create_vector_store_tool()

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        return self._vector_func(action, **kwargs)

    async def _arun(self, action: str, **kwargs) -> Dict[str, Any]:
        return self._run(action, **kwargs)


# Vector search tool with proper Pydantic annotations  
class VectorSearchTool(BaseTool):
    name: str = Field(default="vector_search", description="The name of the tool")
    description: str = Field(
        default="Searches the vector store for similar content",
        description="Description of what the tool does"
    )
    args_schema: Type[BaseModel] = VectorSearchInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._search_func = create_vector_search_tool()

    def _run(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        return self._search_func(query, k)

    async def _arun(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        return self._run(query, k)


# Create function-based tools
def create_vector_store_tool():
    """Create a vector store operations tool"""
    
    def vector_operations(action: str, **kwargs) -> Dict[str, Any]:
        """Perform vector store operations"""
        try:
            if action == "store_documents":
                return _store_documents(**kwargs)
            elif action == "similarity_search":
                return _similarity_search(**kwargs)
            elif action == "get_document_count":
                return _get_document_count(**kwargs)
            else:
                return {"error": f"Unknown vector store action: {action}"}
        except Exception as e:
            return {"error": f"Vector store operation failed: {str(e)}"}
    
    return vector_operations


def create_vector_search_tool():
    """Create a vector search tool"""
    
    def vector_search(query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            return _similarity_search(query=query, k=k)
        except Exception as e:
            return [{"error": f"Vector search failed: {str(e)}"}]
    
    return vector_search


# Helper functions
def _get_vector_store():
    """Initialize and return the vector store"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        vector_store = SupabaseVectorStore(
            client=supabase,
            embedding=embeddings,
            table_name="documents",
            query_name="match_documents"
        )
        
        return vector_store
    except Exception as e:
        raise Exception(f"Failed to initialize vector store: {str(e)}")


def _store_documents(documents: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """Store documents in vector store"""
    try:
        vector_store = _get_vector_store()
        
        # Convert dicts to Document objects
        docs = []
        for doc_data in documents:
            doc = Document(
                page_content=doc_data.get("content", ""),
                metadata=doc_data.get("metadata", {})
            )
            docs.append(doc)
        
        if docs:
            vector_store.add_documents(docs)
            return {"success": True, "message": f"Stored {len(docs)} documents"}
        else:
            return {"error": "No documents to store"}
            
    except Exception as e:
        return {"error": f"Failed to store documents: {str(e)}"}


def _similarity_search(query: str = None, k: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """Perform similarity search"""
    try:
        vector_store = _get_vector_store()
        
        if query:
            results = vector_store.similarity_search(query, k=k)
            
            formatted_results = []
            for i, doc in enumerate(results):
                formatted_results.append({
                    "rank": i + 1,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": getattr(doc, 'score', None)  # Some vector stores include relevance scores
                })
            
            return formatted_results
        else:
            return [{"error": "No query provided for similarity search"}]
            
    except Exception as e:
        return [{"error": f"Similarity search failed: {str(e)}"}]


def _get_document_count(**kwargs) -> Dict[str, Any]:
    """Get document count from vector store"""
    try:
        # This would depend on your specific vector store implementation
        # For SupabaseVectorStore, you might need to query directly
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
        
        response = supabase.table("documents").select("id", count="exact").execute()
        count = response.count if hasattr(response, 'count') else len(response.data)
        
        return {"success": True, "count": count}
        
    except Exception as e:
        return {"error": f"Failed to get document count: {str(e)}"}
=======
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorStoreTool(BaseTool):
    """Tool for creating and managing vector stores for semantic search"""
    
    name = "vector_store"
    description = "Create and query vector stores for semantic document search"
    
    def __init__(self, embeddings: HuggingFaceEmbeddings):
        super().__init__()
        self.embeddings = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Perform vector store operations based on action type"""
        try:
            if action == "create":
                return self._create_vectorstore(**kwargs)
            elif action == "query":
                return self._query_vectorstore(**kwargs)
            elif action == "add_documents":
                return self._add_documents(**kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Vector store operation failed: {str(e)}"}

    def _create_vectorstore(self, texts: List[str], persist_directory: str, metadata: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Create a new vector store from texts"""
        try:
            # Split texts into chunks
            all_chunks = []
            all_metadata = []
            
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                all_chunks.extend(chunks)
                
                # Add metadata for each chunk
                base_metadata = metadata[i] if metadata and i < len(metadata) else {}
                chunk_metadata = []
                for j, chunk in enumerate(chunks):
                    chunk_meta = base_metadata.copy()
                    chunk_meta.update({"chunk_id": j, "source_text_id": i})
                    chunk_metadata.append(chunk_meta)
                
                all_metadata.extend(chunk_metadata)
            
            # Create vector store
            vectorstore = Chroma.from_texts(
                texts=all_chunks,
                embedding=self.embeddings,
                metadatas=all_metadata,
                persist_directory=persist_directory
            )
            
            # Persist the vector store
            vectorstore.persist()
            
            return {
                "success": True,
                "vectorstore_path": persist_directory,
                "total_chunks": len(all_chunks),
                "message": f"Vector store created with {len(all_chunks)} chunks"
            }
            
        except Exception as e:
            return {"error": f"Failed to create vector store: {str(e)}"}

    def _query_vectorstore(self, persist_directory: str, query: str, k: int = 5) -> Dict[str, Any]:
        """Query an existing vector store"""
        try:
            if not os.path.exists(persist_directory):
                return {"error": "Vector store does not exist"}
            
            # Load vector store
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            
            # Perform similarity search
            results = vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results)
            }
            
        except Exception as e:
            return {"error": f"Failed to query vector store: {str(e)}"}

    def _add_documents(self, persist_directory: str, texts: List[str], metadata: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Add new documents to an existing vector store"""
        try:
            if not os.path.exists(persist_directory):
                return self._create_vectorstore(texts, persist_directory, metadata)
            
            # Load existing vector store
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
            
            # Process new texts
            all_chunks = []
            all_metadata = []
            
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                all_chunks.extend(chunks)
                
                base_metadata = metadata[i] if metadata and i < len(metadata) else {}
                for j, chunk in enumerate(chunks):
                    chunk_meta = base_metadata.copy()
                    chunk_meta.update({"chunk_id": j, "source_text_id": i, "added_timestamp": "now"})
                    all_metadata.append(chunk_meta)
            
            # Add documents to existing vector store
            vectorstore.add_texts(all_chunks, metadatas=all_metadata)
            vectorstore.persist()
            
            return {
                "success": True,
                "added_chunks": len(all_chunks),
                "message": f"Added {len(all_chunks)} new chunks to vector store"
            }
            
        except Exception as e:
            return {"error": f"Failed to add documents: {str(e)}"}

    async def _arun(self, action: str, **kwargs) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(action, **kwargs)


class SemanticSearchTool(BaseTool):
    """Advanced tool for semantic search and information retrieval"""
    
    name = "semantic_search"
    description = "Perform advanced semantic search and information retrieval from documents"
    
    def __init__(self, embeddings: HuggingFaceEmbeddings):
        super().__init__()
        self.embeddings = embeddings

    def _run(self, query: str, vectorstore_path: str, search_type: str = "similarity", k: int = 5) -> Dict[str, Any]:
        """Perform semantic search with various search strategies"""
        try:
            if not os.path.exists(vectorstore_path):
                return {"error": "Vector store not found"}
            
            # Load vector store
            vectorstore = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=self.embeddings
            )
            
            # Perform search based on type
            if search_type == "similarity":
                results = vectorstore.similarity_search_with_score(query, k=k)
            elif search_type == "mmr":
                docs = vectorstore.max_marginal_relevance_search(query, k=k)
                results = [(doc, 0.0) for doc in docs]  # MMR doesn't return scores
            else:
                return {"error": f"Unknown search type: {search_type}"}
            
            # Process and rank results
            processed_results = self._process_search_results(results, query)
            
            return {
                "success": True,
                "query": query,
                "search_type": search_type,
                "results": processed_results,
                "total_results": len(processed_results)
            }
            
        except Exception as e:
            return {"error": f"Semantic search failed: {str(e)}"}

    def _process_search_results(self, results: List[tuple], query: str) -> List[Dict[str, Any]]:
        """Process and enrich search results"""
        processed = []
        
        for i, (doc, score) in enumerate(results):
            # Calculate relevance indicators
            content = doc.page_content.lower()
            query_lower = query.lower()
            
            # Simple keyword overlap score
            query_words = set(query_lower.split())
            content_words = set(content.split())
            keyword_overlap = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
            
            processed.append({
                "rank": i + 1,
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score) if score > 0 else None,
                "keyword_overlap": keyword_overlap,
                "content_length": len(doc.page_content),
                "relevance_indicators": {
                    "has_names": any(word.istitle() for word in doc.page_content.split()),
                    "has_contact_info": any(indicator in content for indicator in ["@", "phone", "email"]),
                    "has_dates": any(char.isdigit() for char in doc.page_content),
                }
            })
        
        return processed

    def multi_query_search(self, queries: List[str], vectorstore_path: str, k: int = 3) -> Dict[str, Any]:
        """Perform multiple queries and aggregate results"""
        try:
            all_results = {}
            combined_results = []
            
            for query in queries:
                result = self._run(query, vectorstore_path, k=k)
                if result.get("success"):
                    all_results[query] = result["results"]
                    combined_results.extend(result["results"])
            
            # Remove duplicates and rank by combined relevance
            unique_results = {}
            for result in combined_results:
                content_hash = hash(result["content"])
                if content_hash not in unique_results:
                    unique_results[content_hash] = result
                else:
                    # Combine scores if same content found multiple times
                    existing = unique_results[content_hash]
                    if result.get("similarity_score") and existing.get("similarity_score"):
                        existing["similarity_score"] = max(existing["similarity_score"], result["similarity_score"])
                    existing["keyword_overlap"] = max(existing["keyword_overlap"], result["keyword_overlap"])
            
            final_results = list(unique_results.values())
            final_results.sort(key=lambda x: x.get("similarity_score", 0) + x.get("keyword_overlap", 0), reverse=True)
            
            return {
                "success": True,
                "queries": queries,
                "individual_results": all_results,
                "combined_results": final_results[:k*2],  # Return more results for multi-query
                "total_unique_results": len(final_results)
            }
            
        except Exception as e:
            return {"error": f"Multi-query search failed: {str(e)}"}

    async def _arun(self, query: str, vectorstore_path: str, search_type: str = "similarity", k: int = 5) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(query, vectorstore_path, search_type, k)
>>>>>>> 5ef3108f3d16761ce7924e7b6ff831895e47f517
