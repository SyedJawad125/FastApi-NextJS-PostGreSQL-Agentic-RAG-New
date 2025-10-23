# import os
# from typing import Dict, List, Optional
# import logging
# import numpy as np

# # Configure logging
# logger = logging.getLogger(__name__)

# class VectorStore:
#     """Vector store for document embeddings and similarity search"""
    
#     def __init__(self):
#         """Initialize the vector store"""
#         self.documents: List[str] = []
#         self.metadata: List[Dict] = []
#         self.embeddings: List[List[float]] = []
#         self.index = None
        
#         logger.info("[VECTOR_STORE] Initialized new VectorStore instance")
    
#     def get_count(self) -> int:
#         """Return total number of documents in the vector store"""
#         return len(self.documents)
    
#     def add_document(
#         self,
#         text: str,
#         metadata: Dict,
#         embedding: Optional[List[float]] = None
#     ) -> None:
#         """
#         Add a single document with its metadata and optional embedding
        
#         Args:
#             text: The document text content
#             metadata: Document metadata dictionary
#             embedding: Optional pre-computed embedding vector
#         """
#         try:
#             self.documents.append(text)
#             self.metadata.append(metadata)
            
#             if embedding is not None:
#                 self.embeddings.append(embedding)
                
#                 # Add to FAISS index if available
#                 if self.index is not None:
#                     self.index.add(np.array([embedding], dtype=np.float32))
            
#             logger.debug(f"[VECTOR_STORE] Added document, total count: {len(self.documents)}")
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to add document: {str(e)}")
#             raise
    
#     def get_documents_by_id(self, document_id: str) -> List[Dict]:
#         """
#         Retrieve all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to search for
            
#         Returns:
#             List of dictionaries containing document data
#         """
#         try:
#             results = []
#             for i, meta in enumerate(self.metadata):
#                 if meta.get("document_id") == document_id:
#                     results.append({
#                         "index": i,
#                         "metadata": meta,
#                         "document": self.documents[i],
#                         "content": self.documents[i]
#                     })
            
#             logger.debug(f"[VECTOR_STORE] Found {len(results)} chunks for document_id: {document_id}")
#             return results
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to get documents by ID: {str(e)}")
#             return []
    
#     def _should_filter(self, idx: int, filter_dict: Dict) -> bool:
#         """
#         Check whether a document should be filtered out
        
#         Args:
#             idx: Document index
#             filter_dict: Filter criteria dictionary
            
#         Returns:
#             True if document should be filtered out, False otherwise
#         """
#         meta = self.metadata[idx]
#         for key, value in filter_dict.items():
#             if meta.get(key) != value:
#                 return True
#         return False
    
#     def search_by_embedding(
#         self,
#         query_embedding: List[float],
#         top_k: int = 5,
#         filter: Optional[Dict] = None
#     ) -> List[Dict]:
#         """
#         Search using pre-computed embedding with optional filtering
        
#         Args:
#             query_embedding: Query vector embedding
#             top_k: Number of results to return
#             filter: Optional metadata filter dictionary
            
#         Returns:
#             List of search results with documents, metadata, and scores
#         """
#         try:
#             # Use environment variable for top_k if not specified
#             if top_k is None:
#                 top_k = int(os.getenv("TOP_K_RESULTS", "5"))
            
#             # Handle empty store
#             if len(self.documents) == 0:
#                 logger.warning("[VECTOR_STORE] Search called on empty vector store")
#                 return []
            
#             # Simple cosine similarity search (for stores without FAISS)
#             if self.index is None and len(self.embeddings) > 0:
#                 return self._cosine_similarity_search(query_embedding, top_k, filter)
            
#             # FAISS-based search
#             if self.index is not None:
#                 return self._faiss_search(query_embedding, top_k, filter)
            
#             logger.warning("[VECTOR_STORE] No embeddings or index available for search")
#             return []
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Search by embedding failed: {str(e)}")
#             raise Exception(f"Search by embedding failed: {str(e)}")
    
#     def _cosine_similarity_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform cosine similarity search without FAISS"""
#         query_vec = np.array(query_embedding)
#         similarities = []
        
#         for i, doc_embedding in enumerate(self.embeddings):
#             # Apply filter if specified
#             if filter and self._should_filter(i, filter):
#                 continue
            
#             # Calculate cosine similarity
#             doc_vec = np.array(doc_embedding)
#             similarity = np.dot(query_vec, doc_vec) / (
#                 np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
#             )
#             similarities.append((i, similarity))
        
#         # Sort by similarity (descending)
#         similarities.sort(key=lambda x: x[1], reverse=True)
        
#         # Get top_k results
#         results = []
#         for idx, similarity in similarities[:top_k]:
#             results.append({
#                 "document": self.documents[idx],
#                 "content": self.documents[idx],
#                 "metadata": self.metadata[idx],
#                 "score": float(similarity),
#                 "distance": float(1 - similarity)
#             })
        
#         return results
    
#     def _faiss_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform FAISS-based similarity search"""
#         # Perform similarity search on the FAISS index
#         D, I = self.index.search(
#             np.array([query_embedding], dtype=np.float32),
#             k=min(top_k * 2, len(self.documents))  # Get extra for filtering
#         )
        
#         results = []
#         for i, idx in enumerate(I[0]):
#             if idx < len(self.documents):
#                 # Apply filter if specified
#                 if filter and self._should_filter(idx, filter):
#                     continue
                
#                 results.append({
#                     "document": self.documents[idx],
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(1 - D[0][i]),  # Convert distance to similarity
#                     "distance": float(D[0][i])
#                 })
                
#                 # Stop when we have enough results
#                 if len(results) >= top_k:
#                     break
        
#         return results
    
#     def clear(self) -> None:
#         """Clear all documents from the vector store"""
#         self.documents.clear()
#         self.metadata.clear()
#         self.embeddings.clear()
#         self.index = None
#         logger.info("[VECTOR_STORE] Cleared all documents")
    
#     def remove_document(self, document_id: str) -> int:
#         """
#         Remove all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to remove
            
#         Returns:
#             Number of chunks removed
#         """
#         indices_to_remove = []
        
#         for i, meta in enumerate(self.metadata):
#             if meta.get("document_id") == document_id:
#                 indices_to_remove.append(i)
        
#         # Remove in reverse order to maintain indices
#         for i in sorted(indices_to_remove, reverse=True):
#             del self.documents[i]
#             del self.metadata[i]
#             if i < len(self.embeddings):
#                 del self.embeddings[i]
        
#         # Note: FAISS index would need to be rebuilt after removal
#         if indices_to_remove and self.index is not None:
#             logger.warning("[VECTOR_STORE] FAISS index needs rebuilding after document removal")
#             self.index = None
        
#         logger.info(f"[VECTOR_STORE] Removed {len(indices_to_remove)} chunks for document_id: {document_id}")
#         return len(indices_to_remove)


# # Singleton instance
# _vector_store_instance = None

# def get_vector_store() -> VectorStore:
#     """
#     Get or create the vector store singleton instance
    
#     Returns:
#         VectorStore instance
#     """
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#         logger.info("[VECTOR_STORE] Created new singleton instance")
#     return _vector_store_instance

# def reset_vector_store() -> None:
#     """Reset the vector store singleton (useful for testing)"""
#     global _vector_store_instance
#     _vector_store_instance = None
#     logger.info("[VECTOR_STORE] Reset singleton instance")










# import os
# from typing import Dict, List, Optional
# import logging
# import numpy as np

# # Configure logging
# logger = logging.getLogger(__name__)

# class VectorStore:
#     """Vector store for document embeddings and similarity search"""
    
#     def __init__(self):
#         """Initialize the vector store"""
#         self._reset_storage()
#         logger.info("[VECTOR_STORE] Initialized new VectorStore instance")
    
#     def _reset_storage(self):
#         """Internal method to reset all storage"""
#         self.documents: List[str] = []
#         self.metadata: List[Dict] = []
#         self.embeddings: List[List[float]] = []
#         self.index = None
    
#     def get_count(self) -> int:
#         """Return total number of documents in the vector store"""
#         return len(self.documents)
    
#     def add_document(
#         self,
#         text: str,
#         metadata: Dict,
#         embedding: Optional[List[float]] = None
#     ) -> None:
#         """
#         Add a single document with its metadata and optional embedding
        
#         Args:
#             text: The document text content
#             metadata: Document metadata dictionary
#             embedding: Optional pre-computed embedding vector
#         """
#         try:
#             self.documents.append(text)
#             self.metadata.append(metadata)
            
#             if embedding is not None:
#                 self.embeddings.append(embedding)
                
#                 # Add to FAISS index if available
#                 if self.index is not None:
#                     self.index.add(np.array([embedding], dtype=np.float32))
            
#             logger.debug(f"[VECTOR_STORE] Added document, total count: {len(self.documents)}")
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to add document: {str(e)}")
#             raise
    
#     def get_documents_by_id(self, document_id: str) -> List[Dict]:
#         """
#         Retrieve all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to search for
            
#         Returns:
#             List of dictionaries containing document data
#         """
#         try:
#             results = []
#             for i, meta in enumerate(self.metadata):
#                 if meta.get("document_id") == document_id:
#                     results.append({
#                         "index": i,
#                         "metadata": meta,
#                         "document": self.documents[i],
#                         "content": self.documents[i]
#                     })
            
#             logger.debug(f"[VECTOR_STORE] Found {len(results)} chunks for document_id: {document_id}")
#             return results
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to get documents by ID: {str(e)}")
#             return []
    
#     def _should_filter(self, idx: int, filter_dict: Dict) -> bool:
#         """
#         Check whether a document should be filtered out
        
#         Args:
#             idx: Document index
#             filter_dict: Filter criteria dictionary
            
#         Returns:
#             True if document should be filtered out, False otherwise
#         """
#         meta = self.metadata[idx]
#         for key, value in filter_dict.items():
#             if meta.get(key) != value:
#                 return True
#         return False
    
#     def search_by_embedding(
#         self,
#         query_embedding: List[float],
#         top_k: int = 5,
#         filter: Optional[Dict] = None
#     ) -> List[Dict]:
#         """
#         Search using pre-computed embedding with optional filtering
        
#         Args:
#             query_embedding: Query vector embedding
#             top_k: Number of results to return
#             filter: Optional metadata filter dictionary
            
#         Returns:
#             List of search results with documents, metadata, and scores
#         """
#         try:
#             # Use environment variable for top_k if not specified
#             if top_k is None:
#                 top_k = int(os.getenv("TOP_K_RESULTS", "5"))
            
#             # Handle empty store
#             if len(self.documents) == 0:
#                 logger.warning("[VECTOR_STORE] Search called on empty vector store")
#                 return []
            
#             # Simple cosine similarity search (for stores without FAISS)
#             if self.index is None and len(self.embeddings) > 0:
#                 return self._cosine_similarity_search(query_embedding, top_k, filter)
            
#             # FAISS-based search
#             if self.index is not None:
#                 return self._faiss_search(query_embedding, top_k, filter)
            
#             logger.warning("[VECTOR_STORE] No embeddings or index available for search")
#             return []
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Search by embedding failed: {str(e)}")
#             raise Exception(f"Search by embedding failed: {str(e)}")
    
#     def _cosine_similarity_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform cosine similarity search without FAISS"""
#         query_vec = np.array(query_embedding)
#         similarities = []
        
#         for i, doc_embedding in enumerate(self.embeddings):
#             # Apply filter if specified
#             if filter and self._should_filter(i, filter):
#                 continue
            
#             # Calculate cosine similarity
#             doc_vec = np.array(doc_embedding)
#             similarity = np.dot(query_vec, doc_vec) / (
#                 np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
#             )
#             similarities.append((i, similarity))
        
#         # Sort by similarity (descending)
#         similarities.sort(key=lambda x: x[1], reverse=True)
        
#         # Get top_k results
#         results = []
#         for idx, similarity in similarities[:top_k]:
#             results.append({
#                 "document": self.documents[idx],
#                 "content": self.documents[idx],
#                 "metadata": self.metadata[idx],
#                 "score": float(similarity),
#                 "distance": float(1 - similarity)
#             })
        
#         return results
    
#     def _faiss_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform FAISS-based similarity search"""
#         # Perform similarity search on the FAISS index
#         D, I = self.index.search(
#             np.array([query_embedding], dtype=np.float32),
#             k=min(top_k * 2, len(self.documents))  # Get extra for filtering
#         )
        
#         results = []
#         for i, idx in enumerate(I[0]):
#             if idx < len(self.documents):
#                 # Apply filter if specified
#                 if filter and self._should_filter(idx, filter):
#                     continue
                
#                 results.append({
#                     "document": self.documents[idx],
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(1 - D[0][i]),  # Convert distance to similarity
#                     "distance": float(D[0][i])
#                 })
                
#                 # Stop when we have enough results
#                 if len(results) >= top_k:
#                     break
        
#         return results
    
#     def clear(self) -> None:
#         """Clear all documents from the vector store"""
#         count_before = self.get_count()
        
#         # Explicitly delete references and recreate lists
#         del self.documents
#         del self.metadata
#         del self.embeddings
        
#         # Recreate storage
#         self._reset_storage()
        
#         count_after = self.get_count()
#         logger.info(f"[VECTOR_STORE] Cleared all documents: {count_before} -> {count_after}")
        
#         # Verify it's actually empty
#         if count_after != 0:
#             logger.error(f"[VECTOR_STORE] WARNING: Clear failed! Still has {count_after} items")
#             raise Exception(f"Vector store clear failed: {count_after} items remain")
    
#     def remove_document(self, document_id: str) -> int:
#         """
#         Remove all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to remove
            
#         Returns:
#             Number of chunks removed
#         """
#         indices_to_remove = []
        
#         for i, meta in enumerate(self.metadata):
#             if meta.get("document_id") == document_id:
#                 indices_to_remove.append(i)
        
#         # Remove in reverse order to maintain indices
#         for i in sorted(indices_to_remove, reverse=True):
#             del self.documents[i]
#             del self.metadata[i]
#             if i < len(self.embeddings):
#                 del self.embeddings[i]
        
#         # Note: FAISS index would need to be rebuilt after removal
#         if indices_to_remove and self.index is not None:
#             logger.warning("[VECTOR_STORE] FAISS index needs rebuilding after document removal")
#             self.index = None
        
#         logger.info(f"[VECTOR_STORE] Removed {len(indices_to_remove)} chunks for document_id: {document_id}")
#         return len(indices_to_remove)


# # Singleton instance
# _vector_store_instance = None

# def get_vector_store() -> VectorStore:
#     """
#     Get or create the vector store singleton instance
    
#     Returns:
#         VectorStore instance
#     """
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#         logger.info("[VECTOR_STORE] Created new singleton instance")
#     return _vector_store_instance

# def reset_vector_store() -> None:
#     """Reset the vector store singleton (useful for testing)"""
#     global _vector_store_instance
    
#     # Clear the existing instance if it exists
#     if _vector_store_instance is not None:
#         try:
#             _vector_store_instance.clear()
#         except Exception as e:
#             logger.warning(f"[VECTOR_STORE] Error clearing instance before reset: {e}")
    
#     # Delete the reference
#     _vector_store_instance = None
#     logger.info("[VECTOR_STORE] Reset singleton instance")




# import os
# from typing import Dict, List, Optional
# import logging
# import numpy as np
# import gc  # Garbage collector

# # Configure logging
# logger = logging.getLogger(__name__)

# class VectorStore:
#     """Vector store for document embeddings and similarity search"""
    
#     def __init__(self):
#         """Initialize the vector store"""
#         self.documents: List[str] = []
#         self.metadata: List[Dict] = []
#         self.embeddings: List[List[float]] = []
#         self.index = None
#         self._is_cleared = False
#         logger.info("[VECTOR_STORE] Initialized new VectorStore instance")
    
#     def get_count(self) -> int:
#         """Return total number of documents in the vector store"""
#         if self._is_cleared:
#             return 0
#         return len(self.documents)
    
#     def add_document(
#         self,
#         text: str,
#         metadata: Dict,
#         embedding: Optional[List[float]] = None
#     ) -> None:
#         """
#         Add a single document with its metadata and optional embedding
        
#         Args:
#             text: The document text content
#             metadata: Document metadata dictionary
#             embedding: Optional pre-computed embedding vector
#         """
#         try:
#             # Reset cleared flag when adding new documents
#             self._is_cleared = False
            
#             self.documents.append(text)
#             self.metadata.append(metadata)
            
#             if embedding is not None:
#                 self.embeddings.append(embedding)
                
#                 # Add to FAISS index if available
#                 if self.index is not None:
#                     self.index.add(np.array([embedding], dtype=np.float32))
            
#             logger.debug(f"[VECTOR_STORE] Added document, total count: {len(self.documents)}")
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to add document: {str(e)}")
#             raise
    
#     def get_documents_by_id(self, document_id: str) -> List[Dict]:
#         """
#         Retrieve all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to search for
            
#         Returns:
#             List of dictionaries containing document data
#         """
#         if self._is_cleared:
#             logger.debug("[VECTOR_STORE] Store is cleared, returning empty list")
#             return []
            
#         try:
#             results = []
#             for i, meta in enumerate(self.metadata):
#                 if meta.get("document_id") == document_id:
#                     results.append({
#                         "index": i,
#                         "metadata": meta,
#                         "document": self.documents[i],
#                         "content": self.documents[i]
#                     })
            
#             logger.debug(f"[VECTOR_STORE] Found {len(results)} chunks for document_id: {document_id}")
#             return results
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Failed to get documents by ID: {str(e)}")
#             return []
    
#     def _should_filter(self, idx: int, filter_dict: Dict) -> bool:
#         """
#         Check whether a document should be filtered out
        
#         Args:
#             idx: Document index
#             filter_dict: Filter criteria dictionary
            
#         Returns:
#             True if document should be filtered out, False otherwise
#         """
#         meta = self.metadata[idx]
#         for key, value in filter_dict.items():
#             if meta.get(key) != value:
#                 return True
#         return False
    
#     def search_by_embedding(
#         self,
#         query_embedding: List[float],
#         top_k: int = 5,
#         filter: Optional[Dict] = None
#     ) -> List[Dict]:
#         """
#         Search using pre-computed embedding with optional filtering
        
#         Args:
#             query_embedding: Query vector embedding
#             top_k: Number of results to return
#             filter: Optional metadata filter dictionary
            
#         Returns:
#             List of search results with documents, metadata, and scores
#         """
#         # Check if store is cleared
#         if self._is_cleared or len(self.documents) == 0:
#             logger.warning("[VECTOR_STORE] Search called on cleared/empty vector store")
#             return []
            
#         try:
#             # Use environment variable for top_k if not specified
#             if top_k is None:
#                 top_k = int(os.getenv("TOP_K_RESULTS", "5"))
            
#             # Simple cosine similarity search (for stores without FAISS)
#             if self.index is None and len(self.embeddings) > 0:
#                 return self._cosine_similarity_search(query_embedding, top_k, filter)
            
#             # FAISS-based search
#             if self.index is not None:
#                 return self._faiss_search(query_embedding, top_k, filter)
            
#             logger.warning("[VECTOR_STORE] No embeddings or index available for search")
#             return []
            
#         except Exception as e:
#             logger.error(f"[VECTOR_STORE] Search by embedding failed: {str(e)}")
#             raise Exception(f"Search by embedding failed: {str(e)}")
    
#     def _cosine_similarity_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform cosine similarity search without FAISS"""
#         if self._is_cleared:
#             return []
            
#         query_vec = np.array(query_embedding)
#         similarities = []
        
#         for i, doc_embedding in enumerate(self.embeddings):
#             # Apply filter if specified
#             if filter and self._should_filter(i, filter):
#                 continue
            
#             # Calculate cosine similarity
#             doc_vec = np.array(doc_embedding)
#             similarity = np.dot(query_vec, doc_vec) / (
#                 np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
#             )
#             similarities.append((i, similarity))
        
#         # Sort by similarity (descending)
#         similarities.sort(key=lambda x: x[1], reverse=True)
        
#         # Get top_k results
#         results = []
#         for idx, similarity in similarities[:top_k]:
#             results.append({
#                 "document": self.documents[idx],
#                 "content": self.documents[idx],
#                 "metadata": self.metadata[idx],
#                 "score": float(similarity),
#                 "distance": float(1 - similarity)
#             })
        
#         return results
    
#     def _faiss_search(
#         self,
#         query_embedding: List[float],
#         top_k: int,
#         filter: Optional[Dict]
#     ) -> List[Dict]:
#         """Perform FAISS-based similarity search"""
#         if self._is_cleared:
#             return []
            
#         # Perform similarity search on the FAISS index
#         D, I = self.index.search(
#             np.array([query_embedding], dtype=np.float32),
#             k=min(top_k * 2, len(self.documents))  # Get extra for filtering
#         )
        
#         results = []
#         for i, idx in enumerate(I[0]):
#             if idx < len(self.documents):
#                 # Apply filter if specified
#                 if filter and self._should_filter(idx, filter):
#                     continue
                
#                 results.append({
#                     "document": self.documents[idx],
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(1 - D[0][i]),  # Convert distance to similarity
#                     "distance": float(D[0][i])
#                 })
                
#                 # Stop when we have enough results
#                 if len(results) >= top_k:
#                     break
        
#         return results
    
#     def clear(self) -> None:
#         """Clear all documents from the vector store"""
#         count_before = len(self.documents)
        
#         logger.info(f"[VECTOR_STORE] Clearing {count_before} documents...")
        
#         # Mark as cleared FIRST
#         self._is_cleared = True
        
#         # Clear all data structures
#         self.documents.clear()
#         self.metadata.clear()
#         self.embeddings.clear()
#         self.index = None
        
#         # Force garbage collection
#         gc.collect()
        
#         count_after = len(self.documents)
#         logger.info(f"[VECTOR_STORE] Cleared: {count_before} -> {count_after}, _is_cleared={self._is_cleared}")
        
#         if count_after != 0:
#             logger.error(f"[VECTOR_STORE] ERROR: Clear failed! Still has {count_after} items")
#             raise Exception(f"Vector store clear failed: {count_after} items remain")
    
#     def remove_document(self, document_id: str) -> int:
#         """
#         Remove all chunks for a specific document ID
        
#         Args:
#             document_id: The document ID to remove
            
#         Returns:
#             Number of chunks removed
#         """
#         if self._is_cleared:
#             return 0
            
#         indices_to_remove = []
        
#         for i, meta in enumerate(self.metadata):
#             if meta.get("document_id") == document_id:
#                 indices_to_remove.append(i)
        
#         # Remove in reverse order to maintain indices
#         for i in sorted(indices_to_remove, reverse=True):
#             del self.documents[i]
#             del self.metadata[i]
#             if i < len(self.embeddings):
#                 del self.embeddings[i]
        
#         # Note: FAISS index would need to be rebuilt after removal
#         if indices_to_remove and self.index is not None:
#             logger.warning("[VECTOR_STORE] FAISS index needs rebuilding after document removal")
#             self.index = None
        
#         logger.info(f"[VECTOR_STORE] Removed {len(indices_to_remove)} chunks for document_id: {document_id}")
#         return len(indices_to_remove)


# # Singleton instance
# _vector_store_instance = None

# def get_vector_store() -> VectorStore:
#     """
#     Get or create the vector store singleton instance
    
#     Returns:
#         VectorStore instance
#     """
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#         logger.info("[VECTOR_STORE] Created new singleton instance")
#     else:
#         # Log current state for debugging
#         count = _vector_store_instance.get_count()
#         is_cleared = _vector_store_instance._is_cleared
#         logger.debug(f"[VECTOR_STORE] Returning existing instance: count={count}, cleared={is_cleared}")
    
#     return _vector_store_instance

# def reset_vector_store() -> None:
#     """Reset the vector store singleton (useful for testing)"""
#     global _vector_store_instance
    
#     logger.info("[VECTOR_STORE] Resetting singleton...")
    
#     # Clear the existing instance if it exists
#     if _vector_store_instance is not None:
#         try:
#             _vector_store_instance.clear()
#             logger.info("[VECTOR_STORE] Cleared existing instance")
#         except Exception as e:
#             logger.warning(f"[VECTOR_STORE] Error clearing instance before reset: {e}")
    
#     # Force delete the instance
#     old_instance_id = id(_vector_store_instance) if _vector_store_instance else None
#     _vector_store_instance = None
    
#     # Force garbage collection
#     gc.collect()
    
#     logger.info(f"[VECTOR_STORE] Reset complete. Old instance ID: {old_instance_id}")
    
# def force_new_vector_store() -> VectorStore:
#     """Force create a completely new vector store instance (for testing)"""
#     global _vector_store_instance
    
#     logger.warning("[VECTOR_STORE] FORCE creating new instance!")
    
#     # Delete old instance
#     if _vector_store_instance is not None:
#         try:
#             _vector_store_instance.clear()
#         except:
#             pass
    
#     _vector_store_instance = None
#     gc.collect()
    
#     # Create new instance
#     _vector_store_instance = VectorStore()
#     logger.info(f"[VECTOR_STORE] Force created new instance: ID={id(_vector_store_instance)}")
    
#     return _vector_store_instance









import os
from typing import Dict, List, Optional
import logging
import numpy as np
import gc  # Garbage collector

# Configure logging
logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document embeddings and similarity search"""
    
    def __init__(self):
        """Initialize the vector store"""
        self.documents: List[str] = []
        self.metadata: List[Dict] = []
        self.embeddings: List[List[float]] = []
        self.index = None
        self._is_cleared = False
        logger.info("[VECTOR_STORE] Initialized new VectorStore instance")
    
    def get_count(self) -> int:
        """Return total number of documents in the vector store"""
        if self._is_cleared:
            return 0
        return len(self.documents)
    
    def add_document(
        self,
        text: str,
        metadata: Dict,
        embedding: Optional[List[float]] = None
    ) -> None:
        """
        Add a single document with its metadata and optional embedding
        
        Args:
            text: The document text content
            metadata: Document metadata dictionary
            embedding: Optional pre-computed embedding vector
        """
        try:
            # Reset cleared flag when adding new documents
            self._is_cleared = False
            
            self.documents.append(text)
            self.metadata.append(metadata)
            
            if embedding is not None:
                self.embeddings.append(embedding)
                
                # Add to FAISS index if available
                if self.index is not None:
                    self.index.add(np.array([embedding], dtype=np.float32))
            
            logger.debug(f"[VECTOR_STORE] Added document, total count: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"[VECTOR_STORE] Failed to add document: {str(e)}")
            raise
    
    def get_documents_by_id(self, document_id: str) -> List[Dict]:
        """
        Retrieve all chunks for a specific document ID
        
        Args:
            document_id: The document ID to search for
            
        Returns:
            List of dictionaries containing document data
        """
        if self._is_cleared:
            logger.debug("[VECTOR_STORE] Store is cleared, returning empty list")
            return []
            
        try:
            results = []
            for i, meta in enumerate(self.metadata):
                if meta.get("document_id") == document_id:
                    results.append({
                        "index": i,
                        "metadata": meta,
                        "document": self.documents[i],
                        "content": self.documents[i]
                    })
            
            logger.debug(f"[VECTOR_STORE] Found {len(results)} chunks for document_id: {document_id}")
            return results
            
        except Exception as e:
            logger.error(f"[VECTOR_STORE] Failed to get documents by ID: {str(e)}")
            return []
    
    def _should_filter(self, idx: int, filter_dict: Dict) -> bool:
        """
        Check whether a document should be filtered out
        
        Args:
            idx: Document index
            filter_dict: Filter criteria dictionary
            
        Returns:
            True if document should be filtered out, False otherwise
        """
        meta = self.metadata[idx]
        for key, value in filter_dict.items():
            if meta.get(key) != value:
                return True
        return False
    
    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search using pre-computed embedding with optional filtering
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filter: Optional metadata filter dictionary
            
        Returns:
            List of search results with documents, metadata, and scores
        """
        # Check if store is cleared
        if self._is_cleared or len(self.documents) == 0:
            logger.warning("[VECTOR_STORE] Search called on cleared/empty vector store")
            return []
            
        try:
            # Use environment variable for top_k if not specified
            if top_k is None:
                top_k = int(os.getenv("TOP_K_RESULTS", "5"))
            
            # Simple cosine similarity search (for stores without FAISS)
            if self.index is None and len(self.embeddings) > 0:
                return self._cosine_similarity_search(query_embedding, top_k, filter)
            
            # FAISS-based search
            if self.index is not None:
                return self._faiss_search(query_embedding, top_k, filter)
            
            logger.warning("[VECTOR_STORE] No embeddings or index available for search")
            return []
            
        except Exception as e:
            logger.error(f"[VECTOR_STORE] Search by embedding failed: {str(e)}")
            raise Exception(f"Search by embedding failed: {str(e)}")
    
    def _cosine_similarity_search(
        self,
        query_embedding: List[float],
        top_k: int,
        filter: Optional[Dict]
    ) -> List[Dict]:
        """Perform cosine similarity search without FAISS"""
        if self._is_cleared:
            return []
            
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, doc_embedding in enumerate(self.embeddings):
            # Apply filter if specified
            if filter and self._should_filter(i, filter):
                continue
            
            # Calculate cosine similarity
            doc_vec = np.array(doc_embedding)
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
            )
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top_k results
        results = []
        for idx, similarity in similarities[:top_k]:
            results.append({
                "document": self.documents[idx],
                "content": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(similarity),
                "distance": float(1 - similarity)
            })
        
        return results
    
    def _faiss_search(
        self,
        query_embedding: List[float],
        top_k: int,
        filter: Optional[Dict]
    ) -> List[Dict]:
        """Perform FAISS-based similarity search"""
        if self._is_cleared:
            return []
            
        # Perform similarity search on the FAISS index
        D, I = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            k=min(top_k * 2, len(self.documents))  # Get extra for filtering
        )
        
        results = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.documents):
                # Apply filter if specified
                if filter and self._should_filter(idx, filter):
                    continue
                
                results.append({
                    "document": self.documents[idx],
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(1 - D[0][i]),  # Convert distance to similarity
                    "distance": float(D[0][i])
                })
                
                # Stop when we have enough results
                if len(results) >= top_k:
                    break
        
        return results
    
    def clear(self) -> None:
        """Clear all documents from the vector store"""
        count_before = len(self.documents)
        
        logger.info(f"[VECTOR_STORE] Clearing {count_before} documents...")
        
        # Mark as cleared FIRST
        self._is_cleared = True
        
        # Clear all data structures
        self.documents.clear()
        self.metadata.clear()
        self.embeddings.clear()
        self.index = None
        
        # Force garbage collection
        gc.collect()
        
        count_after = len(self.documents)
        logger.info(f"[VECTOR_STORE] Cleared: {count_before} -> {count_after}, _is_cleared={self._is_cleared}")
        
        if count_after != 0:
            logger.error(f"[VECTOR_STORE] ERROR: Clear failed! Still has {count_after} items")
            raise Exception(f"Vector store clear failed: {count_after} items remain")
    
    def remove_document(self, document_id: str) -> int:
        """
        Remove all chunks for a specific document ID
        
        Args:
            document_id: The document ID to remove
            
        Returns:
            Number of chunks removed
        """
        if self._is_cleared:
            return 0
            
        indices_to_remove = []
        
        for i, meta in enumerate(self.metadata):
            if meta.get("document_id") == document_id:
                indices_to_remove.append(i)
        
        # Remove in reverse order to maintain indices
        for i in sorted(indices_to_remove, reverse=True):
            del self.documents[i]
            del self.metadata[i]
            if i < len(self.embeddings):
                del self.embeddings[i]
        
        # Note: FAISS index would need to be rebuilt after removal
        if indices_to_remove and self.index is not None:
            logger.warning("[VECTOR_STORE] FAISS index needs rebuilding after document removal")
            self.index = None
        
        logger.info(f"[VECTOR_STORE] Removed {len(indices_to_remove)} chunks for document_id: {document_id}")
        return len(indices_to_remove)


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """
    Get or create the vector store singleton instance
    
    Returns:
        VectorStore instance
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
        logger.info("[VECTOR_STORE] Created new singleton instance")
    else:
        # Log current state for debugging
        count = _vector_store_instance.get_count()
        is_cleared = _vector_store_instance._is_cleared
        logger.debug(f"[VECTOR_STORE] Returning existing instance: count={count}, cleared={is_cleared}")
    
    return _vector_store_instance

def reset_vector_store() -> None:
    """Reset the vector store singleton (useful for testing)"""
    global _vector_store_instance
    
    logger.info("[VECTOR_STORE] Resetting singleton...")
    
    # Clear the existing instance if it exists
    if _vector_store_instance is not None:
        try:
            _vector_store_instance.clear()
            logger.info("[VECTOR_STORE] Cleared existing instance")
        except Exception as e:
            logger.warning(f"[VECTOR_STORE] Error clearing instance before reset: {e}")
    
    # Force delete the instance
    old_instance_id = id(_vector_store_instance) if _vector_store_instance else None
    _vector_store_instance = None
    
    # Force garbage collection
    gc.collect()
    
    logger.info(f"[VECTOR_STORE] Reset complete. Old instance ID: {old_instance_id}")
    
def force_new_vector_store() -> VectorStore:
    """Force create a completely new vector store instance (for testing)"""
    global _vector_store_instance
    
    logger.warning("[VECTOR_STORE] FORCE creating new instance!")
    
    # Delete old instance
    if _vector_store_instance is not None:
        try:
            _vector_store_instance.clear()
        except:
            pass
    
    _vector_store_instance = None
    gc.collect()
    
    # Create new instance
    _vector_store_instance = VectorStore()
    logger.info(f"[VECTOR_STORE] Force created new instance: ID={id(_vector_store_instance)}")
    
    return _vector_store_instance