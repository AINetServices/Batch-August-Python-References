"""
Custom tools for vector store operations and semantic search.
"""

import os
import json
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