# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# from typing import List

# from app.core.config import settings

# # Initialize embedding model
# embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

# # FAISS index
# dimension = embedding_model.get_sentence_embedding_dimension()
# index = faiss.IndexFlatL2(dimension)
# documents: List[str] = []

# def add_document_to_index(text: str):
#     embeddings = embedding_model.encode([text])
#     index.add(np.array(embeddings, dtype=np.float32))
#     documents.append(text)

# def search_similar_documents(query: str, k: int = 2):
#     if len(documents) == 0:
#         return []
#     q_emb = embedding_model.encode([query])
#     D, I = index.search(np.array(q_emb, dtype=np.float32), k=k)
#     return [documents[i] for i in I[0]]


# def get_count():
#     """Get total number of documents in vector store"""
#     return len(documents)

# def clear():
#     """Clear all documents and reset index"""
#     global index, documents
#     index.reset()
#     documents.clear()




# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# from typing import List
# from app.core.config import settings

# class VectorStore:
#     def __init__(self):
#         self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
#         self.dimension = self.embedding_model.get_sentence_embedding_dimension()
#         self.index = faiss.IndexFlatL2(self.dimension)
#         self.documents: List[str] = []
#         self.metadata: List[dict] = []
    
#     def add_document(self, text: str, metadata: dict = None):
#         """Add a document to the index"""
#         embeddings = self.embedding_model.encode([text])
#         self.index.add(np.array(embeddings, dtype=np.float32))
#         self.documents.append(text)
#         self.metadata.append(metadata or {})
    
#     def search(self, query: str, k: int = 2):
#         """Search for similar documents"""
#         if len(self.documents) == 0:
#             return []
        
#         q_emb = self.embedding_model.encode([query])
#         D, I = self.index.search(np.array(q_emb, dtype=np.float32), k=k)
        
#         results = []
#         for idx in I[0]:
#             if idx < len(self.documents):
#                 results.append({
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(D[0][len(results)])
#                 })
#         return results
    
#     def get_count(self):
#         """Get total number of documents"""
#         # Return the actual FAISS index count, not just the documents list
#         return self.index.ntotal
    
#     def clear(self):
#         """Clear all documents and reset index"""
#         # Reset FAISS index by removing all vectors
#         self.index.reset()
        
#         # Clear the documents and metadata lists
#         self.documents.clear()
#         self.metadata.clear()
        
#         count_after = self.get_count()
#         print(f"✅ Vector store cleared. Count: {count_after}")
        
#         # Verify it's actually cleared
#         if count_after != 0:
#             raise Exception(f"Failed to clear vector store: {count_after} vectors remain")
        
#         return True

# # Global singleton instance
# _vector_store_instance = None

# def get_vector_store():
#     """Get or create the singleton vector store instance"""
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#     return _vector_store_instance

# # Backward compatibility functions
# def add_document_to_index(text: str, metadata: dict = None):
#     return get_vector_store().add_document(text, metadata)

# def search_similar_documents(query: str, k: int = 2):
#     return get_vector_store().search(query, k)

# def get_count():
#     return get_vector_store().get_count()

# def clear():
#     return get_vector_store().clear()


# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# from typing import List
# from app.core.config import settings

# class VectorStore:
#     def __init__(self):
#         self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
#         self.dimension = self.embedding_model.get_sentence_embedding_dimension()
#         self.index = faiss.IndexFlatL2(self.dimension)
#         self.documents: List[str] = []
#         self.metadata: List[dict] = []
    
#     def add_document(self, text: str, metadata: dict = None):
#         """Add a document to the index"""
#         embeddings = self.embedding_model.encode([text])
#         self.index.add(np.array(embeddings, dtype=np.float32))
#         self.documents.append(text)
#         self.metadata.append(metadata or {})
    
#     def search(self, query: str, k: int = 2):
#         """Search for similar documents"""
#         if len(self.documents) == 0:
#             return []
        
#         q_emb = self.embedding_model.encode([query])
#         D, I = self.index.search(np.array(q_emb, dtype=np.float32), k=k)
        
#         results = []
#         for idx in I[0]:
#             if idx < len(self.documents):
#                 results.append({
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(D[0][len(results)])
#                 })
#         return results
    
#     def get_count(self):
#         """Get total number of documents"""
#         # Return the actual FAISS index count, not just the documents list
#         return self.index.ntotal
    
#     def clear(self):
#         """Clear all documents and reset index"""
#         # Reset FAISS index by removing all vectors
#         self.index.reset()
        
#         # Clear the documents and metadata lists
#         self.documents.clear()
#         self.metadata.clear()
        
#         count_after = self.get_count()
#         print(f"✅ Vector store cleared. Count: {count_after}")
        
#         # Verify it's actually cleared
#         if count_after != 0:
#             raise Exception(f"Failed to clear vector store: {count_after} vectors remain")
        
#         return True

# # Global singleton instance
# _vector_store_instance = None

# def get_vector_store():
#     """Get or create the singleton vector store instance"""
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#     return _vector_store_instance

# def reset_vector_store():
#     """Reset the singleton instance (forces creation of new vector store)"""
#     global _vector_store_instance
#     _vector_store_instance = None
#     print("🔄 Vector store singleton reset")

# # Backward compatibility functions
# def add_document_to_index(text: str, metadata: dict = None):
#     return get_vector_store().add_document(text, metadata)

# def search_similar_documents(query: str, k: int = 2):
#     return get_vector_store().search(query, k)

# def get_count():
#     return get_vector_store().get_count()

# def clear():
#     return get_vector_store().clear()







# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# from typing import List, Dict, Optional
# from app.core.config import settings

# class VectorStore:
#     def __init__(self):
#         self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
#         self.dimension = self.embedding_model.get_sentence_embedding_dimension()
#         self.index = faiss.IndexFlatL2(self.dimension)
#         self.documents: List[str] = []
#         self.metadata: List[dict] = []
#         self.document_ids: List[str] = []  # Track document IDs for filtering
    
#     def add_document(self, text: str, metadata: dict = None):
#         """Add a document to the index"""
#         embeddings = self.embedding_model.encode([text])
#         self.index.add(np.array(embeddings, dtype=np.float32))
#         self.documents.append(text)
#         self.metadata.append(metadata or {})
#         # Store document_id from metadata for filtering
#         document_id = metadata.get('document_id') if metadata else None
#         self.document_ids.append(document_id)
    
#     def search(self, query: str, k: int = 5, filter: Optional[Dict] = None):
#         """Search for similar documents with optional filtering"""
#         if len(self.documents) == 0:
#             return []
        
#         q_emb = self.embedding_model.encode([query])
#         D, I = self.index.search(np.array(q_emb, dtype=np.float32), k=min(k, len(self.documents)))
        
#         results = []
#         for i, idx in enumerate(I[0]):
#             if idx < len(self.documents):
#                 # Apply filtering if specified
#                 if filter and self._should_filter(idx, filter):
#                     continue
                    
#                 results.append({
#                     "document": self.documents[idx],
#                     "content": self.documents[idx],  # For compatibility
#                     "metadata": self.metadata[idx],
#                     "score": float(1 - D[0][i]),  # Convert distance to similarity score
#                     "distance": float(D[0][i])
#                 })
        
#         return results
    
#     def _should_filter(self, idx: int, filter: Dict) -> bool:
#         """Check if document should be filtered out based on criteria"""
#         if not filter:
#             return False
            
#         metadata = self.metadata[idx]
        
#         # Filter by document_id
#         if 'document_id' in filter and metadata.get('document_id') != filter['document_id']:
#             return True
            
#         # Filter by source/filename
#         if 'source' in filter and metadata.get('source') != filter['source']:
#             return True
            
#         # Filter by content_type
#         if 'content_type' in filter and metadata.get('content_type') != filter['content_type']:
#             return True
            
#         return False
    
#     def search_by_embedding(self, query_embedding: List[float], top_k: int = 5, filter: Optional[Dict] = None):
#         """Search using pre-computed embedding with filtering"""
#         if len(self.documents) == 0:
#             return []
        
#         D, I = self.index.search(np.array([query_embedding], dtype=np.float32), 
#                                 k=min(top_k, len(self.documents)))
        
#         results = []
#         for i, idx in enumerate(I[0]):
#             if idx < len(self.documents):
#                 # Apply filtering if specified
#                 if filter and self._should_filter(idx, filter):
#                     continue
                    
#                 results.append({
#                     "document": self.documents[idx],
#                     "content": self.documents[idx],
#                     "metadata": self.metadata[idx],
#                     "score": float(1 - D[0][i]),  # Convert distance to similarity
#                     "distance": float(D[0][i])
#                 })
        
#         return results
    
#     def get_count(self):
#         """Get total number of documents"""
#         return self.index.ntotal
    
#     def get_documents_by_id(self, document_id: str) -> List[Dict]:
#         """Get all documents for a specific document_id"""
#         results = []
#         for i, metadata in enumerate(self.metadata):
#             if metadata.get('document_id') == document_id:
#                 results.append({
#                     "document": self.documents[i],
#                     "metadata": metadata,
#                     "index": i
#                 })
#         return results
    
#     def clear(self):
#         """Clear all documents and reset index"""
#         self.index.reset()
#         self.documents.clear()
#         self.metadata.clear()
#         self.document_ids.clear()
        
#         count_after = self.get_count()
#         print(f"Vector store cleared. Count: {count_after}")
        
#         if count_after != 0:
#             raise Exception(f"Failed to clear vector store: {count_after} vectors remain")
        
#         return True

# # Global singleton instance
# _vector_store_instance = None

# def get_vector_store():
#     """Get or create the singleton vector store instance"""
#     global _vector_store_instance
#     if _vector_store_instance is None:
#         _vector_store_instance = VectorStore()
#     return _vector_store_instance

# def reset_vector_store():
#     """Reset the singleton instance (forces creation of new vector store)"""
#     global _vector_store_instance
#     _vector_store_instance = None
#     print("Vector store singleton reset")

# # Backward compatibility functions
# def add_document_to_index(text: str, metadata: dict = None):
#     return get_vector_store().add_document(text, metadata)

# def search_similar_documents(query: str, k: int = 5, filter: Optional[Dict] = None):
#     return get_vector_store().search(query, k, filter)

# def get_count():
#     return get_vector_store().get_count()

# def clear():
#     return get_vector_store().clear()







import os
from typing import Dict, List, Optional
from fastapi import logger
import numpy as np

class VectorStore:
    def __init__(self):
        # Store documents and metadata
        self.documents: List[str] = []
        self.metadata: List[Dict] = []
        self.index = None  # FAISS or any other vector index

    def get_count(self) -> int:
        """Return total number of documents in the vector store"""
        return len(self.documents)

    def add_document(self, document: str, metadata: Dict, embedding: List[float]):
        """Add a single document and its metadata"""
        self.documents.append(document)
        self.metadata.append(metadata)
        # Add to FAISS index or whichever index you're using
        if self.index is not None:
            self.index.add(np.array([embedding], dtype=np.float32))

    def get_documents_by_id(self, document_id: str) -> List[Dict]:
        """Retrieve all chunks for a specific document ID"""
        results = []
        for i, meta in enumerate(self.metadata):
            if meta.get("document_id") == document_id:
                results.append({
                    "index": i,
                    "metadata": meta,
                    "document": self.documents[i]
                })
        return results

    def _should_filter(self, idx: int, filter: Dict) -> bool:
        """Helper: check whether the document should be filtered out"""
        meta = self.metadata[idx]
        for key, value in filter.items():
            if meta.get(key) != value:
                return True
        return False

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search using pre-computed embedding with optional filtering"""
        if len(self.documents) == 0 or self.index is None:
            return []

        # Perform similarity search on the index
        D, I = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            k=min(top_k, len(self.documents))
        )

        results = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.documents):
                if filter and self._should_filter(idx, filter):
                    continue
                results.append({
                    "document": self.documents[idx],
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(1 - D[0][i]),  # Convert distance to similarity
                    "distance": float(D[0][i])
                })
        return results



    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search using pre-computed embedding with optional filtering"""
        try:
            top_k = top_k or int(os.getenv("TOP_K_RESULTS", "5"))
            
            # Build where clause for filtering
            where_clause = None
            if filter:
                where_clause = {}
                for key, value in filter.items():
                    where_clause[key] = value
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            # Format results to match the expected format
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "document": results["documents"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {},
                    "score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                    "distance": results["distances"][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search by embedding failed: {str(e)}")
            raise Exception(f"Search by embedding failed: {str(e)}")
    
    def get_documents_by_id(self, document_id: str) -> List[Dict]:
        """Retrieve all chunks for a specific document ID"""
        try:
            # Query for all documents with this document_id
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            formatted_results = []
            for i in range(len(results["documents"])):
                formatted_results.append({
                    "index": i,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    "document": results["documents"][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to get documents by ID: {str(e)}")
            return []