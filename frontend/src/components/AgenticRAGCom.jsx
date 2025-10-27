// 'use client';
// import React, { useState, useEffect } from 'react';
// import { ToastContainer, toast } from 'react-toastify';
// import 'react-toastify/dist/ReactToastify.css';
// import AxiosInstance from "@/components/AxiosInstance";


// // API Configuration
// // const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// const RAGSystem = () => {
//   const [activeTab, setActiveTab] = useState('query');
//   const [isLoading, setIsLoading] = useState(false);

//   // Query State
//   const [queryText, setQueryText] = useState('');
//   const [strategy, setStrategy] = useState('agentic');
//   const [topK, setTopK] = useState(15);
//   const [selectedDocument, setSelectedDocument] = useState('');
//   const [queryResult, setQueryResult] = useState(null);
//   const [queryHistory, setQueryHistory] = useState([]);

//   // Upload State
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [uploadProgress, setUploadProgress] = useState(0);
//   const [documents, setDocuments] = useState([]);

//   // Statistics State
//   const [stats, setStats] = useState({
//     total_documents: 0,
//     total_queries: 0,
//     total_chunks: 0,
//     average_processing_time: 0
//   });

//   // Load data on mount
//   useEffect(() => {
//     // loadDocuments();
//     loadQueryHistory();
//     // loadStats();
//   }, []);

//   // Load documents from API
// //   const loadDocuments = async () => {
// //     try {
// //       const response = await AxiosInstance.get(`/api/rag/documents`);
// //       setDocuments(response.data.documents || []);
// //     } catch (error) {
// //       console.error('Failed to load documents:', error);
// //     }
// //   };

//   // Load query history from localStorage
//   const loadQueryHistory = () => {
//     const saved = localStorage.getItem('ragQueryHistory');
//     if (saved) {
//       setQueryHistory(JSON.parse(saved));
//     }
//   };

//   // Save query to history
//   const saveQueryToHistory = (query) => {
//     const newHistory = [{
//       id: Date.now().toString(),
//       query: query.query,
//       answer: query.answer,
//       strategy: query.strategy_used,
//       processing_time: query.processing_time,
//       confidence_score: query.confidence_score,
//       timestamp: new Date().toLocaleString()
//     }, ...queryHistory.slice(0, 19)]; // Keep last 20

//     setQueryHistory(newHistory);
//     localStorage.setItem('ragQueryHistory', JSON.stringify(newHistory));
//   };

// //   // Load statistics
// //   const loadStats = async () => {
// //     try {
// //       const response = await AxiosInstance.get(`/api/rag/stats`);
// //       setStats(response.data);
// //     } catch (error) {
// //       console.error('Failed to load stats:', error);
// //     }
// //   };

//   // Handle Query Submit
//   const handleQuery = async () => {
//     if (!queryText.trim()) {
//       toast.warning('Please enter a query');
//       return;
//     }

//     setIsLoading(true);
//     try {
//       const requestData = {
//         query: queryText,
//         strategy: strategy,
//         top_k: topK,
//         document_id: selectedDocument || null
//       };

//       const response = await AxiosInstance.post(
//         `/api/rag/query`,
//         requestData,
//         {
//           headers: {
//             'Content-Type': 'application/json',
//           },
//         }
//       );

//       const result = response.data;
//       setQueryResult(result);
//       saveQueryToHistory(result);
//       toast.success('Query completed successfully!');
//       loadStats(); // Refresh stats
//     } catch (error) {
//       console.error('Query error:', error);
//       const errorMessage = error.response?.data?.detail || 'Query failed';
//       toast.error(errorMessage);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleFileUpload = async () => {
//     if (!selectedFile) {
//       toast.warning('Please select a file');
//       return;
//     }

//     const formData = new FormData();
//     formData.append('file', selectedFile);

//     setIsLoading(true);
//     setUploadProgress(0);

//     try {
//       // ✅ FIXED: Correct endpoint path
//       const response = await AxiosInstance.post(
//         `/api/rag/upload`,
//         formData,
//         {
//           headers: {
//             'Content-Type': 'multipart/form-data',
//           },
//           onUploadProgress: (progressEvent) => {
//             const progress = progressEvent.total 
//               ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
//               : 0;
//             setUploadProgress(progress);
//           }
//         }
//       );

//       toast.success(`File uploaded successfully! ${response.data.chunks_created} chunks created`);
//       setSelectedFile(null);
//       setUploadProgress(0);
//       loadDocuments();
//       loadStats();
//     } catch (error) {
//       console.error('Upload error:', error);
      
//       // Enhanced error logging
//       if (error.response) {
//         console.error('Response status:', error.response.status);
//         console.error('Response data:', error.response.data);
//         const errorMessage = error.response?.data?.detail || `Upload failed: ${error.response.status}`;
//         toast.error(errorMessage);
//       } else if (error.request) {
//         console.error('No response received:', error.request);
//         toast.error('No response from server. Check if backend is running.');
//       } else {
//         console.error('Error message:', error.message);
//         toast.error(`Upload failed: ${error.message}`);
//       }
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // Delete Document
//   const handleDeleteDocument = async (documentId, filename) => {
//     if (!confirm(`Delete "${filename}"?`)) return;

//     try {
//       await AxiosInstance.delete(`/api/rag/documents/${documentId}`);
//       toast.success('Document deleted successfully');
//       loadDocuments();
//       loadStats();
//     } catch (error) {
//       toast.error(error.response?.data?.detail || 'Delete failed');
//     }
//   };

//   // Clear All Documents
//   const handleClearAllDocuments = async () => {
//     if (!confirm('⚠️ WARNING: This will permanently delete ALL documents and vectors. Continue?')) {
//       return;
//     }

//     setIsLoading(true);
//     try {
//       const response = await AxiosInstance.delete(`/api/rag/documents/clear`);
//       toast.success(response.data.message);
//       loadDocuments();
//       loadStats();
//     } catch (error) {
//       toast.error(error.response?.data?.detail || 'Clear failed');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // Clear History
//   const clearHistory = () => {
//     setQueryHistory([]);
//     localStorage.removeItem('ragQueryHistory');
//     toast.info('Query history cleared');
//   };

//   // Format file size
//   const formatFileSize = (bytes) => {
//     if (bytes === 0) return '0 Bytes';
//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 py-12 px-4">
//       <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
//       <div className="max-w-7xl mx-auto">
//         {/* Header */}
//         <div className="text-center mb-12">
//           <h1 className="text-4xl font-light text-white mb-2">RAG SYSTEM</h1>
//           <div className="w-24 h-1 bg-gradient-to-r from-blue-400 to-purple-600 mx-auto mb-4"></div>
//           <p className="text-gray-300 max-w-2xl mx-auto">
//             Retrieval-Augmented Generation System with Multi-Agent Architecture
//           </p>
//         </div>

//         {/* Statistics Cards */}
//         <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
//           <div className="bg-gray-800 rounded-lg p-4">
//             <div className="text-3xl font-bold text-blue-400">{stats.total_documents}</div>
//             <div className="text-gray-400 text-sm">Documents</div>
//           </div>
//           <div className="bg-gray-800 rounded-lg p-4">
//             <div className="text-3xl font-bold text-green-400">{stats.total_chunks}</div>
//             <div className="text-gray-400 text-sm">Chunks</div>
//           </div>
//           <div className="bg-gray-800 rounded-lg p-4">
//             <div className="text-3xl font-bold text-purple-400">{stats.total_queries}</div>
//             <div className="text-gray-400 text-sm">Queries</div>
//           </div>
//           <div className="bg-gray-800 rounded-lg p-4">
//             <div className="text-3xl font-bold text-yellow-400">
//               {stats.average_processing_time.toFixed(2)}s
//             </div>
//             <div className="text-gray-400 text-sm">Avg Time</div>
//           </div>
//         </div>

//         {/* Navigation Tabs */}
//         <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
//           {[
//             { id: 'query', label: 'Query', icon: '🔍' },
//             { id: 'upload', label: 'Upload', icon: '📤' },
//             { id: 'documents', label: 'Documents', icon: '📁' },
//             { id: 'history', label: 'History', icon: '📜' },
//             { id: 'info', label: 'Info', icon: 'ℹ️' }
//           ].map((tab) => (
//             <button
//               key={tab.id}
//               onClick={() => setActiveTab(tab.id)}
//               className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
//                 activeTab === tab.id
//                   ? 'bg-blue-600 text-white'
//                   : 'text-gray-300 hover:bg-gray-700 hover:text-white'
//               }`}
//             >
//               <span>{tab.icon}</span>
//               <span className="hidden sm:inline">{tab.label}</span>
//             </button>
//           ))}
//         </div>

//         {/* Query Tab */}
//         {activeTab === 'query' && (
//           <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <span>🔍</span> Query Documents
//             </h2>
            
//             <div className="grid md:grid-cols-2 gap-8">
//               <div className="space-y-6">
//                 <div>
//                   <label className="block text-gray-300 mb-2">Your Question</label>
//                   <textarea
//                     value={queryText}
//                     onChange={(e) => setQueryText(e.target.value)}
//                     placeholder="e.g., Who is Syed Haider Ali and what are his skills?"
//                     rows={4}
//                     className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
//                   />
//                 </div>

//                 <div className="grid grid-cols-2 gap-4">
//                   <div>
//                     <label className="block text-gray-300 mb-2">Strategy</label>
//                     <select
//                       value={strategy}
//                       onChange={(e) => setStrategy(e.target.value)}
//                       className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
//                     >
//                       <option value="simple">Simple</option>
//                       <option value="agentic">Agentic</option>
//                       <option value="auto">Auto</option>
//                     </select>
//                   </div>

//                   <div>
//                     <label className="block text-gray-300 mb-2">Top K Results</label>
//                     <input
//                       type="number"
//                       min="1"
//                       max="50"
//                       value={topK}
//                       onChange={(e) => setTopK(parseInt(e.target.value))}
//                       className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
//                     />
//                   </div>
//                 </div>

//                 <div>
//                   <label className="block text-gray-300 mb-2">
//                     Document Filter (Optional)
//                   </label>
//                   <select
//                     value={selectedDocument}
//                     onChange={(e) => setSelectedDocument(e.target.value)}
//                     className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
//                   >
//                     <option value="">All Documents</option>
//                     {documents.map((doc) => (
//                       <option key={doc.id} value={doc.id}>
//                         {doc.filename}
//                       </option>
//                     ))}
//                   </select>
//                 </div>

//                 <button
//                   onClick={handleQuery}
//                   disabled={isLoading}
//                   className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
//                 >
//                   {isLoading ? (
//                     <>
//                       <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
//                       Processing...
//                     </>
//                   ) : (
//                     <>
//                       <span>🚀</span> Submit Query
//                     </>
//                   )}
//                 </button>
//               </div>

//               <div className="space-y-6">
//                 {queryResult && (
//                   <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-6 border border-blue-500">
//                     <div className="flex items-center justify-between mb-4">
//                       <h3 className="text-xl text-white flex items-center gap-2">
//                         <span>💡</span> Answer
//                       </h3>
//                       <div className="flex items-center gap-2">
//                         <span className="text-xs text-gray-400">
//                           {queryResult.processing_time.toFixed(2)}s
//                         </span>
//                         {queryResult.confidence_score && (
//                           <span className="text-xs text-green-400">
//                             {(queryResult.confidence_score * 100).toFixed(0)}% confidence
//                           </span>
//                         )}
//                       </div>
//                     </div>
                    
//                     <div className="text-gray-200 mb-4 whitespace-pre-wrap">
//                       {queryResult.answer}
//                     </div>

//                     <div className="border-t border-gray-600 pt-4">
//                       <div className="flex items-center justify-between text-sm">
//                         <span className="text-gray-400">Strategy:</span>
//                         <span className="text-blue-400">{queryResult.strategy_used}</span>
//                       </div>
//                       <div className="flex items-center justify-between text-sm mt-2">
//                         <span className="text-gray-400">Chunks Retrieved:</span>
//                         <span className="text-purple-400">
//                           {queryResult.retrieved_chunks.length}
//                         </span>
//                       </div>
//                     </div>
//                   </div>
//                 )}

//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <h4 className="text-white mb-3">💡 Query Tips</h4>
//                   <ul className="text-gray-300 text-sm space-y-1">
//                     <li>• Use specific questions for better results</li>
//                     <li>• Agentic strategy provides detailed analysis</li>
//                     <li>• Filter by document for targeted queries</li>
//                     <li>• Increase Top K for more context</li>
//                   </ul>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Upload Tab */}
//         {activeTab === 'upload' && (
//           <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <span>📤</span> Upload Documents
//             </h2>
            
//             <div className="max-w-2xl mx-auto space-y-6">
//               <div className="bg-gray-700 rounded-lg p-8 border-2 border-dashed border-gray-600">
//                 <input
//                   type="file"
//                   accept=".pdf,.txt,.docx"
//                   onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
//                   className="hidden"
//                   id="file-upload"
//                 />
//                 <label
//                   htmlFor="file-upload"
//                   className="cursor-pointer flex flex-col items-center"
//                 >
//                   <div className="text-6xl mb-4">📄</div>
//                   <div className="text-white text-lg mb-2">
//                     Click to select file
//                   </div>
//                   <div className="text-gray-400 text-sm">
//                     Supported: PDF, TXT, DOCX (Max 50MB)
//                   </div>
//                 </label>
//               </div>

//               {selectedFile && (
//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <div className="flex items-center justify-between mb-2">
//                     <div className="flex items-center gap-3">
//                       <span className="text-2xl">📄</span>
//                       <div>
//                         <div className="text-white font-medium">{selectedFile.name}</div>
//                         <div className="text-gray-400 text-sm">
//                           {formatFileSize(selectedFile.size)}
//                         </div>
//                       </div>
//                     </div>
//                     <button
//                       onClick={() => setSelectedFile(null)}
//                       className="text-red-400 hover:text-red-300"
//                     >
//                       ✕
//                     </button>
//                   </div>

//                   {uploadProgress > 0 && (
//                     <div className="mt-3">
//                       <div className="flex items-center justify-between text-sm text-gray-400 mb-1">
//                         <span>Uploading...</span>
//                         <span>{uploadProgress}%</span>
//                       </div>
//                       <div className="w-full bg-gray-600 rounded-full h-2">
//                         <div
//                           className="bg-blue-600 h-2 rounded-full transition-all"
//                           style={{ width: `${uploadProgress}%` }}
//                         />
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               )}

//               <button
//                 onClick={handleFileUpload}
//                 disabled={!selectedFile || isLoading}
//                 className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
//               >
//                 {isLoading ? (
//                   <>
//                     <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
//                     Uploading...
//                   </>
//                 ) : (
//                   <>
//                     <span>☁️</span> Upload Document
//                   </>
//                 )}
//               </button>

//               <div className="bg-gray-700 rounded-lg p-4">
//                 <h4 className="text-white mb-3">📋 Processing Steps</h4>
//                 <ol className="text-gray-300 text-sm space-y-2">
//                   <li>1️⃣ Document is uploaded and validated</li>
//                   <li>2️⃣ Text is extracted from the file</li>
//                   <li>3️⃣ Content is split into chunks</li>
//                   <li>4️⃣ Embeddings are generated</li>
//                   <li>5️⃣ Vectors are stored in ChromaDB</li>
//                   <li>6️⃣ Ready for querying!</li>
//                 </ol>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Documents Tab */}
//         {activeTab === 'documents' && (
//           <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
//             <div className="flex items-center justify-between mb-6">
//               <h2 className="text-2xl text-white flex items-center gap-2">
//                 <span>📁</span> Document Library ({documents.length})
//               </h2>
//               {documents.length > 0 && (
//                 <button
//                   onClick={handleClearAllDocuments}
//                   className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
//                 >
//                   🗑️ Clear All
//                 </button>
//               )}
//             </div>
            
//             {documents.length > 0 ? (
//               <div className="space-y-4">
//                 {documents.map((doc) => (
//                   <div
//                     key={doc.id}
//                     className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors"
//                   >
//                     <div className="flex items-start justify-between">
//                       <div className="flex items-start gap-3 flex-1">
//                         <span className="text-3xl">📄</span>
//                         <div className="flex-1">
//                           <div className="text-white font-medium mb-1">
//                             {doc.filename}
//                           </div>
//                           <div className="flex flex-wrap gap-3 text-sm">
//                             <span className="text-gray-400">
//                               {formatFileSize(doc.size)}
//                             </span>
//                             <span className="text-blue-400">
//                               {doc.chunks_count} chunks
//                             </span>
//                             <span className={`${
//                               doc.status === 'completed' ? 'text-green-400' : 'text-yellow-400'
//                             }`}>
//                               {doc.status}
//                             </span>
//                             <span className="text-gray-400">
//                               {new Date(doc.uploaded_at).toLocaleDateString()}
//                             </span>
//                           </div>
//                         </div>
//                       </div>
//                       <button
//                         onClick={() => handleDeleteDocument(doc.id, doc.filename)}
//                         className="ml-4 p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded"
//                       >
//                         🗑️
//                       </button>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             ) : (
//               <div className="text-center text-gray-400 py-12">
//                 <div className="text-6xl mb-4">📁</div>
//                 <p className="text-xl">No documents uploaded</p>
//                 <p className="mt-2">Upload documents to start querying</p>
//                 <button
//                   onClick={() => setActiveTab('upload')}
//                   className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
//                 >
//                   Upload Now
//                 </button>
//               </div>
//             )}
//           </div>
//         )}

//         {/* History Tab */}
//         {activeTab === 'history' && (
//           <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
//             <div className="flex items-center justify-between mb-6">
//               <h2 className="text-2xl text-white flex items-center gap-2">
//                 <span>📜</span> Query History
//               </h2>
//               {queryHistory.length > 0 && (
//                 <button
//                   onClick={clearHistory}
//                   className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
//                 >
//                   Clear History
//                 </button>
//               )}
//             </div>
            
//             {queryHistory.length > 0 ? (
//               <div className="space-y-4">
//                 {queryHistory.map((query) => (
//                   <div
//                     key={query.id}
//                     className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500"
//                   >
//                     <div className="flex items-start justify-between mb-3">
//                       <span className="text-gray-400 text-sm">{query.timestamp}</span>
//                       <div className="flex items-center gap-2 text-xs">
//                         <span className="text-blue-400">{query.strategy}</span>
//                         <span className="text-gray-400">
//                           {query.processing_time.toFixed(2)}s
//                         </span>
//                       </div>
//                     </div>
                    
//                     <div className="mb-3">
//                       <div className="text-white font-medium mb-2">
//                         Q: {query.query}
//                       </div>
//                       <div className="text-gray-300 text-sm">
//                         A: {query.answer.substring(0, 200)}
//                         {query.answer.length > 200 && '...'}
//                       </div>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             ) : (
//               <div className="text-center text-gray-400 py-12">
//                 <div className="text-6xl mb-4">📜</div>
//                 <p className="text-xl">No query history</p>
//                 <p className="mt-2">Start querying to see your history</p>
//               </div>
//             )}
//           </div>
//         )}

//         {/* Info Tab */}
//         {activeTab === 'info' && (
//           <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <span>ℹ️</span> System Information
//             </h2>
            
//             <div className="grid md:grid-cols-2 gap-8">
//               <div className="space-y-6">
//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <h3 className="text-lg text-white mb-3">🧠 RAG Strategies</h3>
//                   <div className="space-y-3 text-sm">
//                     <div>
//                       <div className="text-blue-400 font-medium">Simple</div>
//                       <div className="text-gray-300">
//                         Basic vector search and retrieval
//                       </div>
//                     </div>
//                     <div>
//                       <div className="text-purple-400 font-medium">Agentic</div>
//                       <div className="text-gray-300">
//                         Multi-agent system with reasoning
//                       </div>
//                     </div>
//                     <div>
//                       <div className="text-green-400 font-medium">Auto</div>
//                       <div className="text-gray-300">
//                         Automatically selects best strategy
//                       </div>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <h3 className="text-lg text-white mb-3">🔧 Technologies</h3>
//                   <div className="space-y-2 text-sm">
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">LLM:</span>
//                       <span className="text-blue-400">Groq</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Vector Store:</span>
//                       <span className="text-blue-400">ChromaDB</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Database:</span>
//                       <span className="text-blue-400">PostgreSQL</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Framework:</span>
//                       <span className="text-blue-400">FastAPI</span>
//                     </div>
//                   </div>
//                 </div>
//               </div>

//               <div className="space-y-6">
//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <h3 className="text-lg text-white mb-3">📚 Supported Formats</h3>
//                   <div className="flex flex-wrap gap-2">
//                     {['PDF', 'TXT', 'DOCX', 'MD'].map((format) => (
//                       <span
//                         key={format}
//                         className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm"
//                       >
//                         {format}
//                       </span>
//                     ))}
//                   </div>
//                 </div>

//                 <div className="bg-gray-700 rounded-lg p-4">
//                   <h3 className="text-lg text-white mb-3">✨ Features</h3>
//                   <ul className="text-gray-300 text-sm space-y-2">
//                     <li>✓ Multi-agent collaboration</li>
//                     <li>✓ Semantic search</li>
//                     <li>✓ Session management</li>
//                     <li>✓ Knowledge graph RAG</li>
//                     <li>✓ ReAct pattern reasoning</li>
//                   </ul>
//                 </div>

//                 <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-4 border border-blue-500">
//                   <h3 className="text-lg text-white mb-2">🚀 Quick Start</h3>
//                   <p className="text-gray-300 text-sm mb-3">
//                     Upload documents and start querying in seconds!
//                   </p>
//                   <button
//                     onClick={() => setActiveTab('upload')}
//                     className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
//                   >
//                     Get Started
//                   </button>
//                 </div>
//               </div>
//             </div>

//             <div className="mt-8 bg-gray-700 rounded-lg p-4">
//               <h3 className="text-lg text-white mb-3">🔗 API Endpoints</h3>
//               <div className="space-y-2 text-sm">
//                 <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
//                   POST /api/rag/query
//                 </div>
//                 <div className="text-gray-300 mb-3">
//                   Query the RAG system with different strategies
//                 </div>
                
//                 <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
//                   POST /api/rag/upload
//                 </div>
//                 <div className="text-gray-300 mb-3">
//                   Upload and process documents (PDF, TXT, DOCX)
//                 </div>
                
//                 <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
//                   GET /api/rag/documents
//                 </div>
//                 <div className="text-gray-300 mb-3">
//                   List all uploaded documents
//                 </div>

//                 <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
//                   DELETE /api/rag/documents/clear
//                 </div>
//                 <div className="text-gray-300">
//                   Clear all documents and vectors
//                 </div>
//               </div>
//             </div>

//             <div className="mt-8 bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-lg p-4 border border-green-500">
//               <h3 className="text-lg text-white mb-3">📖 Example Query</h3>
//               <div className="bg-gray-800 p-3 rounded font-mono text-sm text-gray-300">
//                 <div>&#123;</div>
//                 <div className="ml-4">&quot;query&quot;: &quot;Who is Syed Haider Ali?&quot;,</div>
//                 <div className="ml-4">&quot;strategy&quot;: &quot;agentic&quot;,</div>
//                 <div className="ml-4">&quot;top_k&quot;: 15</div>
//                 <div>&#125;</div>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default RAGSystem;


'use client';
import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AxiosInstance from "@/components/AxiosInstance";

const RAGSystem = () => {
  const [activeTab, setActiveTab] = useState('query');
  const [isLoading, setIsLoading] = useState(false);

  // Query State
  const [queryText, setQueryText] = useState('');
  const [strategy, setStrategy] = useState('agentic');
  const [topK, setTopK] = useState(15);
  const [selectedDocument, setSelectedDocument] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);

  // Upload State
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documents, setDocuments] = useState([]);

  // Statistics State
  const [stats, setStats] = useState({
    total_documents: 0,
    total_queries: 0,
    total_chunks: 0,
    average_processing_time: 0
  });

  // Load data on mount
  useEffect(() => {
    loadDocuments();
    loadQueryHistory();
    loadStats();
  }, []);

  // Load documents from API
  const loadDocuments = async () => {
    try {
      const response = await AxiosInstance.get(`/api/rag/documents`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  // Load query history from localStorage
  const loadQueryHistory = () => {
    const saved = localStorage.getItem('ragQueryHistory');
    if (saved) {
      setQueryHistory(JSON.parse(saved));
    }
  };

  // Save query to history
  const saveQueryToHistory = (query) => {
    const newHistory = [{
      id: Date.now().toString(),
      query: query.query,
      answer: query.answer,
      strategy: query.strategy_used,
      processing_time: query.processing_time,
      confidence_score: query.confidence_score,
      timestamp: new Date().toLocaleString()
    }, ...queryHistory.slice(0, 19)];

    setQueryHistory(newHistory);
    localStorage.setItem('ragQueryHistory', JSON.stringify(newHistory));
  };

  // Load statistics
  const loadStats = async () => {
    try {
      const response = await AxiosInstance.get(`/api/rag/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Handle Query Submit
  const handleQuery = async () => {
    if (!queryText.trim()) {
      toast.warning('Please enter a query');
      return;
    }

    setIsLoading(true);
    try {
      const requestData = {
        query: queryText,
        strategy: strategy,
        top_k: topK,
        document_id: selectedDocument || null
      };

      const response = await AxiosInstance.post(
        `/api/rag/query`,
        requestData,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const result = response.data;
      setQueryResult(result);
      saveQueryToHistory(result);
      toast.success('Query completed successfully!');
      loadStats();
    } catch (error) {
      console.error('Query error:', error);
      const errorMessage = error.response?.data?.detail || 'Query failed';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      toast.warning('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setIsLoading(true);
    setUploadProgress(0);

    try {
      const response = await AxiosInstance.post(
        `/api/rag/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total 
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            setUploadProgress(progress);
          }
        }
      );

      toast.success(`File uploaded successfully! ${response.data.chunks_created} chunks created`);
      setSelectedFile(null);
      setUploadProgress(0);
      loadDocuments();
      loadStats();
    } catch (error) {
      console.error('Upload error:', error);
      
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
        const errorMessage = error.response?.data?.detail || `Upload failed: ${error.response.status}`;
        toast.error(errorMessage);
      } else if (error.request) {
        console.error('No response received:', error.request);
        toast.error('No response from server. Check if backend is running.');
      } else {
        console.error('Error message:', error.message);
        toast.error(`Upload failed: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Delete Document
  const handleDeleteDocument = async (documentId, filename) => {
    if (!confirm(`Delete "${filename}"?`)) return;

    try {
      await AxiosInstance.delete(`/api/rag/documents/${documentId}`);
      toast.success('Document deleted successfully');
      loadDocuments();
      loadStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Delete failed');
    }
  };

  // Clear All Documents
  const handleClearAllDocuments = async () => {
    if (!confirm('⚠️ WARNING: This will permanently delete ALL documents and vectors. Continue?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await AxiosInstance.delete(`/api/rag/documents/clear`);
      toast.success(response.data.message);
      loadDocuments();
      loadStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Clear failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Clear History
  const clearHistory = () => {
    setQueryHistory([]);
    localStorage.removeItem('ragQueryHistory');
    toast.info('Query history cleared');
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 py-12 px-4">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-white mb-2">RAG SYSTEM</h1>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-400 to-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Retrieval-Augmented Generation System with Multi-Agent Architecture
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-3xl font-bold text-blue-400">{stats.total_documents}</div>
            <div className="text-gray-400 text-sm">Documents</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-3xl font-bold text-green-400">{stats.total_chunks}</div>
            <div className="text-gray-400 text-sm">Chunks</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-3xl font-bold text-purple-400">{stats.total_queries}</div>
            <div className="text-gray-400 text-sm">Queries</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-3xl font-bold text-yellow-400">
              {stats.average_processing_time.toFixed(2)}s
            </div>
            <div className="text-gray-400 text-sm">Avg Time</div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
          {[
            { id: 'query', label: 'Query', icon: '🔍' },
            { id: 'upload', label: 'Upload', icon: '📤' },
            { id: 'documents', label: 'Documents', icon: '📁' },
            { id: 'history', label: 'History', icon: '📜' },
            { id: 'info', label: 'Info', icon: 'ℹ️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>🔍</span> Query Documents
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-300 mb-2">Your Question</label>
                  <textarea
                    value={queryText}
                    onChange={(e) => setQueryText(e.target.value)}
                    placeholder="e.g., Who is Syed Haider Ali and what are his skills?"
                    rows={4}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 mb-2">Strategy</label>
                    <select
                      value={strategy}
                      onChange={(e) => setStrategy(e.target.value)}
                      className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="simple">Simple</option>
                      <option value="agentic">Agentic</option>
                      <option value="auto">Auto</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-300 mb-2">Top K Results</label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={topK}
                      onChange={(e) => setTopK(parseInt(e.target.value))}
                      className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">
                    Document Filter (Optional)
                  </label>
                  <select
                    value={selectedDocument}
                    onChange={(e) => setSelectedDocument(e.target.value)}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="">All Documents</option>
                    {documents.map((doc) => (
                      <option key={doc.id} value={doc.id}>
                        {doc.filename}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleQuery}
                  disabled={isLoading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <span>🚀</span> Submit Query
                    </>
                  )}
                </button>
              </div>

              <div className="space-y-6">
                {queryResult && (
                  <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-6 border border-blue-500">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl text-white flex items-center gap-2">
                        <span>💡</span> Answer
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400">
                          {queryResult.processing_time.toFixed(2)}s
                        </span>
                        {queryResult.confidence_score && (
                          <span className="text-xs text-green-400">
                            {(queryResult.confidence_score * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-gray-200 mb-4 whitespace-pre-wrap">
                      {queryResult.answer}
                    </div>

                    <div className="border-t border-gray-600 pt-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Strategy:</span>
                        <span className="text-blue-400">{queryResult.strategy_used}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm mt-2">
                        <span className="text-gray-400">Chunks Retrieved:</span>
                        <span className="text-purple-400">
                          {queryResult.retrieved_chunks.length}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white mb-3">💡 Query Tips</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>• Use specific questions for better results</li>
                    <li>• Agentic strategy provides detailed analysis</li>
                    <li>• Filter by document for targeted queries</li>
                    <li>• Increase Top K for more context</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>📤</span> Upload Documents
            </h2>
            
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="bg-gray-700 rounded-lg p-8 border-2 border-dashed border-gray-600">
                <input
                  type="file"
                  accept=".pdf,.txt,.docx"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  <div className="text-6xl mb-4">📄</div>
                  <div className="text-white text-lg mb-2">
                    Click to select file
                  </div>
                  <div className="text-gray-400 text-sm">
                    Supported: PDF, TXT, DOCX (Max 50MB)
                  </div>
                </label>
              </div>

              {selectedFile && (
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">📄</span>
                      <div>
                        <div className="text-white font-medium">{selectedFile.name}</div>
                        <div className="text-gray-400 text-sm">
                          {formatFileSize(selectedFile.size)}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-red-400 hover:text-red-300"
                    >
                      ✕
                    </button>
                  </div>

                  {uploadProgress > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-sm text-gray-400 mb-1">
                        <span>Uploading...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || isLoading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <span>☁️</span> Upload Document
                  </>
                )}
              </button>

              <div className="bg-gray-700 rounded-lg p-4">
                <h4 className="text-white mb-3">📋 Processing Steps</h4>
                <ol className="text-gray-300 text-sm space-y-2">
                  <li>1️⃣ Document is uploaded and validated</li>
                  <li>2️⃣ Text is extracted from the file</li>
                  <li>3️⃣ Content is split into chunks</li>
                  <li>4️⃣ Embeddings are generated</li>
                  <li>5️⃣ Vectors are stored in ChromaDB</li>
                  <li>6️⃣ Ready for querying!</li>
                </ol>
              </div>
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl text-white flex items-center gap-2">
                <span>📁</span> Document Library ({documents.length})
              </h2>
              {documents.length > 0 && (
                <button
                  onClick={handleClearAllDocuments}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
                >
                  🗑️ Clear All
                </button>
              )}
            </div>
            
            {documents.length > 0 ? (
              <div className="space-y-4">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <span className="text-3xl">📄</span>
                        <div className="flex-1">
                          <div className="text-white font-medium mb-1">
                            {doc.filename}
                          </div>
                          <div className="flex flex-wrap gap-3 text-sm">
                            <span className="text-gray-400">
                              {formatFileSize(doc.size)}
                            </span>
                            <span className="text-blue-400">
                              {doc.chunks_count} chunks
                            </span>
                            <span className={`${
                              doc.status === 'completed' ? 'text-green-400' : 'text-yellow-400'
                            }`}>
                              {doc.status}
                            </span>
                            <span className="text-gray-400">
                              {new Date(doc.uploaded_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                        className="ml-4 p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">📁</div>
                <p className="text-xl">No documents uploaded</p>
                <p className="mt-2">Upload documents to start querying</p>
                <button
                  onClick={() => setActiveTab('upload')}
                  className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                >
                  Upload Now
                </button>
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl text-white flex items-center gap-2">
                <span>📜</span> Query History
              </h2>
              {queryHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
                >
                  Clear History
                </button>
              )}
            </div>
            
            {queryHistory.length > 0 ? (
              <div className="space-y-4">
                {queryHistory.map((query) => (
                  <div
                    key={query.id}
                    className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <span className="text-gray-400 text-sm">{query.timestamp}</span>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-blue-400">{query.strategy}</span>
                        <span className="text-gray-400">
                          {query.processing_time.toFixed(2)}s
                        </span>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-white font-medium mb-2">
                        Q: {query.query}
                      </div>
                      <div className="text-gray-300 text-sm">
                        A: {query.answer.substring(0, 200)}
                        {query.answer.length > 200 && '...'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">📜</div>
                <p className="text-xl">No query history</p>
                <p className="mt-2">Start querying to see your history</p>
              </div>
            )}
          </div>
        )}

        {/* Info Tab */}
        {activeTab === 'info' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>ℹ️</span> System Information
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">🧠 RAG Strategies</h3>
                  <div className="space-y-3 text-sm">
                    <div>
                      <div className="text-blue-400 font-medium">Simple</div>
                      <div className="text-gray-300">
                        Basic vector search and retrieval
                      </div>
                    </div>
                    <div>
                      <div className="text-purple-400 font-medium">Agentic</div>
                      <div className="text-gray-300">
                        Multi-agent system with reasoning
                      </div>
                    </div>
                    <div>
                      <div className="text-green-400 font-medium">Auto</div>
                      <div className="text-gray-300">
                        Automatically selects best strategy
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">🔧 Technologies</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">LLM:</span>
                      <span className="text-blue-400">Groq</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Vector Store:</span>
                      <span className="text-blue-400">ChromaDB</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Database:</span>
                      <span className="text-blue-400">PostgreSQL</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Framework:</span>
                      <span className="text-blue-400">FastAPI</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">📚 Supported Formats</h3>
                  <div className="flex flex-wrap gap-2">
                    {['PDF', 'TXT', 'DOCX', 'MD'].map((format) => (
                      <span
                        key={format}
                        className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm"
                      >
                        {format}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">✨ Features</h3>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>✓ Multi-agent collaboration</li>
                    <li>✓ Semantic search</li>
                    <li>✓ Session management</li>
                    <li>✓ Knowledge graph RAG</li>
                    <li>✓ ReAct pattern reasoning</li>
                  </ul>
                </div>

                <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-4 border border-blue-500">
                  <h3 className="text-lg text-white mb-2">🚀 Quick Start</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Upload documents and start querying in seconds!
                  </p>
                  <button
                    onClick={() => setActiveTab('upload')}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
                  >
                    Get Started
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-8 bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg text-white mb-3">🔗 API Endpoints</h3>
              <div className="space-y-2 text-sm">
                <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
                  POST /api/rag/query
                </div>
                <div className="text-gray-300 mb-3">
                  Query the RAG system with different strategies
                </div>
                
                <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
                  POST /api/rag/upload
                </div>
                <div className="text-gray-300 mb-3">
                  Upload and process documents (PDF, TXT, DOCX)
                </div>
                
                <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
                  GET /api/rag/documents
                </div>
                <div className="text-gray-300 mb-3">
                  List all uploaded documents
                </div>

                <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
                  DELETE /api/rag/documents/clear
                </div>
                <div className="text-gray-300">
                  Clear all documents and vectors
                </div>
              </div>
            </div>

            <div className="mt-8 bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-lg p-4 border border-green-500">
              <h3 className="text-lg text-white mb-3">📖 Example Query</h3>
              <div className="bg-gray-800 p-3 rounded font-mono text-sm text-gray-300">
                <div>&#123;</div>
                <div className="ml-4">&quot;query&quot;: &quot;Who is Syed Haider Ali?&quot;,</div>
                <div className="ml-4">&quot;strategy&quot;: &quot;agentic&quot;,</div>
                <div className="ml-4">&quot;top_k&quot;: 15</div>
                <div>&#125;</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RAGSystem;