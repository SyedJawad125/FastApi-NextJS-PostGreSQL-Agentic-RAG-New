# ============================================================
# 🧠 RAG Query Endpoint (FIXED)
# ============================================================
from app.core.dependencies import get_vectorstore
# @router.post("/query", response_model=RAGQueryResponse)
# async def query_rag(request: RAGQueryRequest, db: Session = Depends(get_db)):
#     """Main RAG query endpoint with strategy support and data safety checks."""
#     try:
#         logger.info(f"[QUERY] Received query: {request.query[:50]}...")
#         start_time = time.time()

#         # ✅ CORRECT: Get the RAG orchestrator (not vector store directly!)
#         from app.services.orchestrator import get_rag_orchestrator
#         from app.core.enums import RAGStrategy
#         from app.services.vectorstore import get_vector_store
        
#         rag_service = get_rag_orchestrator()
#         vector_store = get_vectorstore()  # Just for safety checks
        
#         # ✅ CRITICAL SAFETY CHECK: Verify database AND vector store have data
#         total_docs = db.query(Document).count()
#         total_chunks = db.query(DocumentChunk).count()
#         vector_count = vector_store.get_count()
#         is_cleared = vector_store._is_cleared
        
#         logger.info(
#             f"[DATABASE] Current state: {total_docs} docs, {total_chunks} chunks, "
#             f"{vector_count} vectors (cleared={is_cleared})"
#         )
        
#         # ✅ IMMEDIATE REJECTION if no data exists
#         if (total_docs == 0 and total_chunks == 0) or vector_count == 0 or is_cleared:
#             logger.warning("[SAFETY] No documents/vectors in system - rejecting query")
#             return RAGQueryResponse(
#                 query=request.query,
#                 answer="No documents found in the system. Please upload CVs first.",
#                 strategy_used="direct",
#                 processing_time=0.1,
#                 retrieved_chunks=[],
#                 confidence_score=0.0
#             )

#         # ✅ Map strategy string to enum
#         strategy_map = {
#             "simple": RAGStrategy.SIMPLE,
#             "agentic": RAGStrategy.AGENTIC,
#             "auto": RAGStrategy.AUTO
#         }

#         if request.strategy not in strategy_map:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid strategy: {request.strategy}. Use: simple, agentic, or auto"
#             )

#         strategy = strategy_map[request.strategy]

#         # ✅ Validate document exists if document_id is provided
#         document_id = request.document_id
#         document = None
#         if document_id:
#             document = db.query(Document).filter(Document.id == document_id).first()
#             if not document:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Document with ID {document_id} not found"
#                 )
#             logger.info(f"[QUERY] Querying document: {document.filename}")

#         # ✅ Execute RAG query using YOUR orchestrator
#         result = await rag_service.execute_query(
#             query=request.query,
#             top_k=request.top_k,
#             session_id=request.session_id,
#             document_id=document_id,
#             strategy=strategy
#         )

#         processing_time = time.time() - start_time

#         # ✅ Enhanced logging for debugging
#         retrieved_chunks = result.get("retrieved_chunks", [])
#         logger.info(
#             f"[QUERY] Retrieved {len(retrieved_chunks)} chunks, "
#             f"processing time: {processing_time:.2f}s, "
#             f"source: {result.get('source', 'unknown')}, "
#             f"fallback: {result.get('fallback_used', False)}"
#         )

#         # ✅ Save query in DB with document_id and enhanced metadata
#         db_query = Query(
#             id=str(uuid.uuid4()),
#             query_text=request.query,
#             answer=result["answer"],
#             strategy_used=request.strategy,
#             processing_time=processing_time,
#             confidence_score=result.get("confidence", 0.85),
#             retrieved_chunks_count=len(retrieved_chunks),
#             session_id=request.session_id,
#             document_id=document_id,
#             metadata={
#                 "top_k": request.top_k,
#                 "chunk_count": len(retrieved_chunks),
#                 "document_id": document_id,
#                 "document_filename": document.filename if document else None,
#                 "database_docs_count": total_docs,
#                 "database_chunks_count": total_chunks,
#                 "vector_store_count": vector_count,
#                 "source": result.get("source", "vector_database"),
#                 "fallback_used": result.get("fallback_used", False),
#                 "max_relevance_score": result.get("max_relevance_score", 0.0),
#                 "agent_steps": result.get("agent_steps", [])
#             }
#         )
#         db.add(db_query)
#         db.commit()
#         db.refresh(db_query)

#         logger.info(f"[QUERY] Successfully processed query with {request.strategy} strategy")

#         return RAGQueryResponse(
#             query=request.query,
#             answer=result["answer"],
#             strategy_used=result["strategy_used"].value,
#             processing_time=processing_time,
#             retrieved_chunks=retrieved_chunks,
#             confidence_score=result.get("confidence", 0.85)
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"[ERROR] Query processing failed: {str(e)}", exc_info=True)
#         db.rollback()
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Query processing failed: {str(e)}"
#         )



        # Save query in DB with enhanced metadata
# ============================================================
# 🧹 Clear All Documents Endpoint (FIXED)
# ============================================================
# @router.delete("/documents/clear")
# async def clear_all_documents(db: Session = Depends(get_db)):
#     """
#     [DANGER] Danger Zone: Permanently delete all uploaded documents 
#     and clear vector stores.
#     """
#     try:
#         from app.models.rag_model import Query
#         from app.services.vectorstore import get_vector_store, reset_vector_store
        
#         # Count before deleting
#         total_docs = db.query(Document).count()
#         total_chunks = db.query(DocumentChunk).count()
#         total_queries = db.query(Query).count()
        
#         logger.info(f"[STATS] Before deletion: {total_docs} docs, {total_chunks} chunks, {total_queries} queries")
        
#         # 🧠 STEP 1: Clear vector stores
#         vector_count_before = 0
#         # 🧹 STEP 1: Clear vector stores - ENHANCED
#         try:
#             logger.info("[CLEAR] Step 1: Clearing vector stores...")
            
#             # Get vector store and count
#             vector_store = get_vector_store()
#             vector_count_before = vector_store.get_count()
            
#             logger.info(f"[VECTOR_STORE] Vector count before clear: {vector_count_before}")
            
#             # Clear using the fixed method
#             vector_store.clear()
            
#             # Force a completely new instance to be sure
#             reset_vector_store(force_new=True)
            
#             # Verify it's actually cleared
#             vector_store = get_vector_store()
#             vector_count_after = vector_store.get_count()
            
#             logger.info(f"[VECTOR_STORE] Vector count after clear: {vector_count_after}")
            
#             if vector_count_after != 0:
#                 logger.error(f"[ERROR] Vector store not fully cleared! Still has {vector_count_after} items")
#                 raise Exception(f"Vector store clear incomplete: {vector_count_after} items remain")
            
#             logger.info(f"[SUCCESS] Vector store cleared: {vector_count_before} vectors removed")
            
#         except Exception as e:
#             logger.error(f"[ERROR] Vector store clear failed: {str(e)}", exc_info=True)
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to clear vector store: {str(e)}"
#             )
        
#         # 🧹 STEP 2: Delete from database
#         deleted_docs = 0
#         deleted_chunks = 0
#         deleted_queries = 0
        
#         try:
#             logger.info("[CLEAR] Step 2: Deleting from database...")
            
#             # Delete queries FIRST (no foreign keys pointing to it)
#             logger.info(f"[DELETE] Deleting {total_queries} queries...")
#             deleted_queries = db.query(Query).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_queries} queries")
            
#             # Delete chunks (has foreign key to documents)
#             logger.info(f"[DELETE] Deleting {total_chunks} chunks...")
#             deleted_chunks = db.query(DocumentChunk).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_chunks} chunks")
            
#             # Delete documents (must be last)
#             logger.info(f"[DELETE] Deleting {total_docs} documents...")
#             deleted_docs = db.query(Document).delete(synchronize_session=False)
#             db.flush()
#             logger.info(f"[SUCCESS] Deleted {deleted_docs} documents")
            
#             # Commit all changes
#             db.commit()
#             logger.info("[SUCCESS] All database deletions committed")
            
#         except Exception as e:
#             db.rollback()
#             logger.error(f"[ERROR] Database deletion failed: {str(e)}", exc_info=True)
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to delete from database: {str(e)}"
#             )
        
#         # 📊 STEP 3: Final verification
#         remaining_docs = db.query(Document).count()
#         remaining_chunks = db.query(DocumentChunk).count()
#         remaining_queries = db.query(Query).count()
#         remaining_vectors = get_vector_store().get_count()
        
#         logger.info(
#             f"[STATS] After deletion: {remaining_docs} docs, "
#             f"{remaining_chunks} chunks, {remaining_queries} queries, "
#             f"{remaining_vectors} vectors"
#         )
        
#         # Check if anything remains
#         if any([remaining_docs, remaining_chunks, remaining_queries, remaining_vectors]):
#             logger.warning("[WARN] Incomplete deletion detected!")
#             return {
#                 "status": "partial_success",
#                 "message": "Some data may not have been fully cleared",
#                 "deleted": {
#                     "documents": deleted_docs,
#                     "chunks": deleted_chunks,
#                     "queries": deleted_queries,
#                     "vectors": vector_count_before
#                 },
#                 "remaining": {
#                     "documents": remaining_docs,
#                     "chunks": remaining_chunks,
#                     "queries": remaining_queries,
#                     "vectors": remaining_vectors
#                 }
#             }
        
#         # Success response
#         return {
#             "status": "success",
#             "message": (
#                 f"Successfully cleared all data: {deleted_docs} documents, "
#                 f"{deleted_chunks} chunks, {deleted_queries} queries, "
#                 f"{vector_count_before} vectors"
#             ),
#             "deleted": {
#                 "documents": deleted_docs,
#                 "chunks": deleted_chunks,
#                 "queries": deleted_queries,
#                 "vectors": vector_count_before
#             },
#             "remaining": {
#                 "documents": 0,
#                 "chunks": 0,
#                 "queries": 0,
#                 "vectors": 0
#             }
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"[ERROR] Failed to clear documents: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to clear documents: {str(e)}"
#         )



# # ============================================================
# # 📤 Document Upload Endpoint
# # ============================================================
# from PyPDF2 import PdfReader

# try:
#     import docx  # python-docx
# except Exception:
#     docx = None


# def extract_text_from_pdf_bytes(pdf_bytes):
#     """Extract text from PDF bytes with enhanced error handling"""
#     try:
#         reader = PdfReader(io.BytesIO(pdf_bytes))
#         text = ""
#         for page_num, page in enumerate(reader.pages):
#             try:
#                 page_text = page.extract_text() or ""
#                 text += page_text
#                 logger.debug(f"[DEBUG] Extracted {len(page_text)} chars from page {page_num + 1}")
#             except Exception as e:
#                 logger.warning(f"[WARN] Failed to extract text from page {page_num + 1}: {str(e)}")
#                 continue
#         return text
#     except Exception as e:
#         logger.error(f"[ERROR] PDF extraction failed: {str(e)}")
#         raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")


# def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
#     """Extract text from DOCX bytes with enhanced error handling"""
#     if docx is None:
#         raise RuntimeError("python-docx is not installed. Install with: pip install python-docx")
    
#     try:
#         doc = docx.Document(io.BytesIO(file_bytes))
#         paragraphs = [p.text for p in doc.paragraphs if p.text]
#         text = "\n".join(paragraphs)
        
#         # Also extract text from tables
#         for table in doc.tables:
#             for row in table.rows:
#                 for cell in row.cells:
#                     if cell.text and cell.text.strip():
#                         text += "\n" + cell.text
        
#         return text.strip()
#     except Exception as e:
#         logger.error(f"[ERROR] DOCX extraction failed: {str(e)}")
#         raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


# def extract_text_from_txt_bytes(file_bytes: bytes) -> str:
#     """Extract text from TXT bytes with enhanced encoding detection"""
#     encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
    
#     for encoding in encodings:
#         try:
#             text = file_bytes.decode(encoding)
#             # Validate that we got meaningful text
#             if text.strip() and any(char.isalnum() for char in text):
#                 logger.debug(f"[DEBUG] Successfully decoded with {encoding}")
#                 return text
#         except UnicodeDecodeError:
#             continue
#         except Exception as e:
#             logger.warning(f"[WARN] Encoding {encoding} failed: {str(e)}")
#             continue
    
#     # Fallback: decode with utf-8 ignoring errors
#     logger.warning("[WARN] All encodings failed, using utf-8 with ignore errors")
#     return file_bytes.decode("utf-8", errors="ignore")


# # ✅ Update the response model to include processing_time as string
# class DocumentUploadResponse(BaseModel):
#     document_id: str
#     filename: str
#     status: str
#     chunks_created: int
#     message: str
#     processing_time: str


# @router.post("/upload", response_model=DocumentUploadResponse)
# async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """Upload and process document for RAG (PDF, TXT, DOCX) with enhanced monitoring and error handling."""
#     start_time = time.time()
#     processing_metrics = {
#         'extraction_time': 0,
#         'chunking_time': 0,
#         'db_operations_time': 0,
#         'vector_store_time': 0,
#         'total_chars_processed': 0
#     }
    
#     try:
#         logger.info(f"[UPLOAD] Received file upload: {file.filename} (Size: {file.size or 'unknown'})")

#         # Validate file type
#         allowed_types = [
#             "application/pdf",
#             "text/plain",
#             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#         ]
        
#         if file.content_type not in allowed_types:
#             # Also check by file extension as fallback
#             file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
#             if file_extension not in ['pdf', 'txt', 'docx']:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"File type not supported. Allowed: PDF, TXT, DOCX. Got: {file.content_type}"
#                 )
#             else:
#                 logger.info(f"[INFO] Using file extension {file_extension} for content type detection")

#         # Read bytes
#         content = await file.read()
#         if len(content) == 0:
#             raise HTTPException(status_code=400, detail="Uploaded file is empty")

#         file_size_mb = len(content) / (1024 * 1024)
#         logger.info(f"[FILE] File size: {len(content)} bytes ({file_size_mb:.2f} MB)")

#         # Extract text based on content type with timing
#         extraction_start = time.time()
#         try:
#             if file.content_type == "application/pdf":
#                 text = extract_text_from_pdf_bytes(content)
#             elif file.content_type == "text/plain":
#                 text = extract_text_from_txt_bytes(content)
#             elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#                 text = extract_text_from_docx_bytes(content)
#             else:
#                 # Fallback: try to detect by extension
#                 if file.filename.lower().endswith('.pdf'):
#                     text = extract_text_from_pdf_bytes(content)
#                 elif file.filename.lower().endswith('.docx'):
#                     text = extract_text_from_docx_bytes(content)
#                 else:
#                     text = extract_text_from_txt_bytes(content)
#         except Exception as e:
#             raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")
        
#         processing_metrics['extraction_time'] = time.time() - extraction_start

#         # Enhanced text validation
#         if not text or text.strip() == "":
#             logger.warning(f"[WARN] No extractable text found in {file.filename}, content type: {file.content_type}")
#             raise HTTPException(status_code=400, detail="No extractable text found in uploaded document")

#         # Check if text is meaningful (not just whitespace/formatting)
#         clean_text = text.strip()
#         if len(clean_text) < 10:
#             logger.warning(f"[WARN] Very little text extracted from {file.filename}: {len(clean_text)} chars")
#             raise HTTPException(status_code=400, detail="Extracted text appears to be too short or invalid")

#         processing_metrics['total_chars_processed'] = len(clean_text)
#         logger.info(f"[TEXT] Extracted {len(clean_text)} characters from document")

#         # Chunk the extracted text with timing
#         chunking_start = time.time()
#         chunks = chunk_text(clean_text)
#         processing_metrics['chunking_time'] = time.time() - chunking_start

#         # Validate chunks
#         if not isinstance(chunks, list):
#             raise HTTPException(status_code=500, detail="chunk_text did not return a list of chunks")

#         if not chunks:
#             raise HTTPException(status_code=400, detail="No chunks generated from document text")

#         if len(chunks) == 0:
#             raise HTTPException(status_code=400, detail="Empty chunks list generated")

#         logger.info(f"[CHUNKS] Generated {len(chunks)} chunks for file {file.filename}")

#         # Calculate chunk statistics
#         chunk_sizes = []
#         for chunk in chunks:
#             chunk_text_content = chunk.get("content") if isinstance(chunk, dict) else chunk
#             if chunk_text_content:
#                 chunk_sizes.append(len(chunk_text_content))

#         if chunk_sizes:
#             logger.info(f"[STATS] Chunk sizes: min={min(chunk_sizes)}, max={max(chunk_sizes)}, avg={sum(chunk_sizes)/len(chunk_sizes):.0f}")

#         # ✅ Create document ID and DB record within transaction
#         doc_id = str(uuid.uuid4())
#         db_operations_start = time.time()
        
#         try:
#             db_doc = Document(
#                 id=doc_id,
#                 filename=file.filename,
#                 content_type=file.content_type,
#                 size=len(content),
#                 status="processing",
#                 chunks_count=0,
#                 uploaded_at=datetime.utcnow(),
#                 meta_data={
#                     "original_size": len(content),
#                     "processing_method": "local_extraction",
#                     "extracted_chars": len(clean_text),
#                     "chunks_generated": len(chunks)
#                 }
#             )
#             db.add(db_doc)
#             db.flush()

#             # Add chunks to vector store and database
#             vector_store = get_vector_store()
#             vector_store_start = time.time()
            
#             chunks_created = 0
#             failed_chunks = 0
#             chunk_details = []

#             for idx, chunk in enumerate(chunks):
#                 try:
#                     chunk_text_content = chunk.get("content") if isinstance(chunk, dict) else chunk
#                     if not chunk_text_content or not chunk_text_content.strip():
#                         logger.warning(f"[WARN] Skipping empty chunk at index {idx}")
#                         failed_chunks += 1
#                         continue

#                     chunk_id = str(uuid.uuid4())

#                     # Create database chunk record
#                     db_chunk = DocumentChunk(
#                         id=chunk_id,
#                         document_id=doc_id,
#                         content=chunk_text_content,
#                         chunk_index=idx,
#                         meta_data={
#                             "source": file.filename,
#                             "content_type": file.content_type,
#                             "chunk_size": len(chunk_text_content),
#                             "chunk_chars": len(chunk_text_content)
#                         },
#                         created_at=datetime.utcnow()
#                     )
#                     db.add(db_chunk)

#                     # Add to vector store
#                     vector_store.add_document(
#                         text=chunk_text_content,
#                         metadata={
#                             "chunk_id": chunk_id,
#                             "chunk_index": idx,
#                             "document_id": doc_id,
#                             "source": file.filename,
#                             "content_type": file.content_type,
#                             "chunk_size": len(chunk_text_content)
#                         }
#                     )
#                     chunks_created += 1
#                     chunk_details.append({
#                         "index": idx,
#                         "size": len(chunk_text_content),
#                         "status": "success"
#                     })

#                 except Exception as e:
#                     logger.error(f"[ERROR] Failed to process chunk {idx}: {str(e)}")
#                     failed_chunks += 1
#                     chunk_details.append({
#                         "index": idx,
#                         "size": len(chunk_text_content) if chunk_text_content else 0,
#                         "status": "failed",
#                         "error": str(e)
#                     })
#                     continue

#             processing_metrics['vector_store_time'] = time.time() - vector_store_start

#             # Update document record
#             db_doc.status = "completed" if chunks_created > 0 else "failed"
#             db_doc.chunks_count = chunks_created
#             db_doc.processed_at = datetime.utcnow()
#             db_doc.meta_data.update({
#                 "chunks_created": chunks_created,
#                 "chunks_failed": failed_chunks,
#                 "processing_metrics": processing_metrics,
#                 "chunk_details": chunk_details
#             })

#             processing_metrics['db_operations_time'] = time.time() - db_operations_start

#             # Commit transaction
#             db.commit()
#             db.refresh(db_doc)

#         except Exception as e:
#             db.rollback()
#             logger.error(f"[ERROR] Database transaction failed: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")

#         # Log final statistics
#         total_processing_time = time.time() - start_time
#         logger.info(f"[SUCCESS] Upload complete: {chunks_created} chunks created, {failed_chunks} failed")
#         logger.info(f"[TIME] Processing times - Total: {total_processing_time:.2f}s, "
#                    f"Extraction: {processing_metrics['extraction_time']:.2f}s, "
#                    f"Chunking: {processing_metrics['chunking_time']:.2f}s, "
#                    f"DB: {processing_metrics['db_operations_time']:.2f}s, "
#                    f"Vector: {processing_metrics['vector_store_time']:.2f}s")

#         # Optional: get vector count
#         try:
#             vector_count = vector_store.get_count()
#             logger.info(f"[VECTOR] Vector store now contains {vector_count} total vectors")
#         except Exception as e:
#             logger.warning(f"[WARN] Could not retrieve vector count: {str(e)}")

#         # ✅ Format processing time as "4.4 seconds"
#         formatted_time = f"{total_processing_time:.1f} seconds"

#         # ✅ Return the response with processing_time as formatted string
#         return DocumentUploadResponse(
#             document_id=db_doc.id,
#             filename=file.filename,
#             status="success",
#             chunks_created=chunks_created,
#             message=f"Document '{file.filename}' processed successfully with {chunks_created} chunks",
#             processing_time=formatted_time
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"[ERROR] Document upload failed: {str(e)}", exc_info=True)
#         try:
#             db.rollback()
#         except Exception:
#             pass  # Already rolled back or no transaction
#         raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")
    