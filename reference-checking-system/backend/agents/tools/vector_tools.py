"""
Custom tools for vector store operations.
"""

import os
from typing import Any, Dict, List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


# Create simple function-based tools
def create_vector_store_tool(embeddings=None):
    """Create a vector store tool"""
    
    def vector_operations(action: str, **kwargs) -> Dict[str, Any]:
        """Perform vector store operations based on action type"""
        try:
            if action == "store_documents":
                return _store_documents(embeddings, **kwargs)
            elif action == "similarity_search":
                return _similarity_search(embeddings, **kwargs)
            elif action == "get_collection_info":
                return _get_collection_info(embeddings, **kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Vector store operation failed: {str(e)}"}
    
    return vector_operations


# Helper functions
def _store_documents(embeddings, documents: List[Document], collection_name: str = "reference_docs") -> Dict[str, Any]:
    """Store documents in vector database"""
    try:
        # Use provided embeddings or create default
        if embeddings is None:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        # Create or load vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="./chroma_db",
            collection_name=collection_name
        )
        
        return {
            "success": True,
            "message": f"Stored {len(documents)} documents in collection '{collection_name}'",
            "collection_size": len(documents)
        }
    except Exception as e:
        return {"error": f"Failed to store documents: {str(e)}"}


def _similarity_search(embeddings, query: str, collection_name: str = "reference_docs", k: int = 5) -> Dict[str, Any]:
    """Perform similarity search in vector database"""
    try:
        # Use provided embeddings or create default
        if embeddings is None:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        # Load vector store
        vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        # Perform search
        results = vector_store.similarity_search(query, k=k)
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results):
            formatted_results.append({
                "rank": i + 1,
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "total_found": len(results)
        }
    except Exception as e:
        return {"error": f"Failed to perform similarity search: {str(e)}"}


def _get_collection_info(embeddings, collection_name: str = "reference_docs") -> Dict[str, Any]:
    """Get information about a vector collection"""
    try:
        # Use provided embeddings or create default
        if embeddings is None:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        # Load vector store
        vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        # Get collection info
        collection = vector_store._collection
        count = collection.count()
        
        return {
            "success": True,
            "collection_name": collection_name,
            "document_count": count,
            "persist_directory": "./chroma_db"
        }
    except Exception as e:
        return {"error": f"Failed to get collection info: {str(e)}"}


# Simple wrapper class
class VectorStoreTool:
    def __init__(self, embeddings=None):
        self.embeddings = embeddings
        self._vector_func = create_vector_store_tool(embeddings)
    
    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        return self._vector_func(action, **kwargs)
