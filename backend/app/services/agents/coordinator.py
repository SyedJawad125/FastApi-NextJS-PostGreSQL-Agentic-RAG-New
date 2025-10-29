"""
Enhanced Coordinator Agent with ReAct Pattern
Decides which tools to use for answering queries
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Master coordinator that implements ReAct pattern:
    1. Reason about the query
    2. Act by selecting appropriate tools/agents
    3. Observe results
    4. Repeat or conclude
    """
    
    def __init__(self, llm_service, embedding_service, vectorstore):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.vectorstore = vectorstore
        
        # Track execution steps for transparency
        self.execution_steps = []
        
        logger.info("[COORDINATOR] Initialized with ReAct pattern")
    
    async def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute query using ReAct pattern
        
        ReAct Loop:
        Thought → Action → Observation → Thought → ... → Answer
        """
        self.execution_steps = []
        start_time = datetime.now()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[COORDINATOR] Starting ReAct execution for: {query}")
        logger.info(f"{'='*80}")
        
        try:
            # Step 1: THOUGHT - Analyze the query
            thought_1 = await self._think_about_query(query, context)
            self._log_step("THOUGHT", thought_1)
            
            # Step 2: ACTION - Search ChromaDB first (always start here)
            action_1 = "Search ChromaDB for uploaded documents"
            self._log_step("ACTION", action_1)
            
            chromadb_result = await self._search_chromadb(query, context)
            self._log_step("OBSERVATION", f"Found {len(chromadb_result['chunks'])} chunks in ChromaDB")
            
            # Step 3: THOUGHT - Is ChromaDB result relevant?
            relevance_check = await self._check_relevance(query, chromadb_result)
            self._log_step("THOUGHT", f"ChromaDB relevance: {relevance_check['verdict']}")
            
            if relevance_check["is_relevant"]:
                # Step 4: ACTION - Generate answer from ChromaDB
                self._log_step("ACTION", "Generate answer from uploaded documents")
                
                answer = await self._generate_answer_from_chromadb(query, chromadb_result)
                self._log_step("OBSERVATION", "Answer generated successfully from documents")
                
                return self._build_response(
                    answer=answer,
                    source="chromadb",
                    chunks=chromadb_result["chunks"],
                    relevance_score=relevance_check["score"]
                )
            
            else:
                # Step 5: THOUGHT - Need external search
                thought_2 = f"Documents not relevant ({relevance_check['reason']}). Need internet search."
                self._log_step("THOUGHT", thought_2)
                
                # Step 6: ACTION - Search internet with Tavily
                self._log_step("ACTION", "Search internet using Tavily AI")
                
                internet_result = await self._search_internet(query)
                self._log_step(
                    "OBSERVATION", 
                    f"Found {len(internet_result.get('results', []))} internet sources"
                )
                
                if internet_result.get("success") and internet_result.get("results"):
                    # Step 7: ACTION - Generate answer from internet
                    self._log_step("ACTION", "Generate answer from internet sources")
                    
                    answer = await self._generate_answer_from_internet(query, internet_result)
                    self._log_step("OBSERVATION", "Answer generated from internet sources")
                    
                    return self._build_response(
                        answer=answer,
                        source="internet",
                        chunks=[],
                        internet_sources=internet_result["results"]
                    )
                
                else:
                    # Step 8: FALLBACK - Use general knowledge
                    self._log_step("THOUGHT", "Internet search failed. Using general knowledge.")
                    self._log_step("ACTION", "Generate answer from LLM general knowledge")
                    
                    answer = await self._generate_answer_from_knowledge(query)
                    self._log_step("OBSERVATION", "Answer generated from general knowledge")
                    
                    return self._build_response(
                        answer=answer,
                        source="general_knowledge",
                        chunks=[]
                    )
        
        except Exception as e:
            logger.error(f"[COORDINATOR ERROR] {str(e)}", exc_info=True)
            self._log_step("ERROR", str(e))
            
            return {
                "answer": f"I encountered an error while processing your query: {str(e)}",
                "source": "error",
                "execution_steps": self.execution_steps,
                "retrieved_chunks": [],
                "confidence": 0.0
            }
        
        finally:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"[COORDINATOR] Execution completed in {execution_time:.2f}s")
            logger.info(f"[COORDINATOR] Total steps: {len(self.execution_steps)}")
    
    async def _think_about_query(self, query: str, context: Dict) -> str:
        """Step 1: Reason about the query"""
        prompt = f"""Analyze this query and determine the best approach to answer it:

Query: "{query}"

Available context:
- ChromaDB has {self.vectorstore.get_count()} documents
- Document ID filter: {context.get('document_id', 'None')}

Think about:
1. Is this likely to be in uploaded documents?
2. Does it require current/recent information?
3. Is it a general knowledge question?

Provide a brief reasoning (2-3 sentences):"""

        thought = await self.llm_service.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=150
        )
        
        return thought.strip()
    
    async def _search_chromadb(self, query: str, context: Dict) -> Dict[str, Any]:
        """Action: Search ChromaDB"""
        try:
            query_embedding = self.embedding_service.embed_text(query)
            
            filter_params = None
            if context.get("document_id"):
                filter_params = {"document_id": context["document_id"]}
            
            results = self.vectorstore.search_by_embedding(
                query_embedding=query_embedding,
                top_k=context.get("top_k", 5),
                filter=filter_params
            )
            
            return {
                "success": True,
                "chunks": results,
                "count": len(results)
            }
        
        except Exception as e:
            logger.error(f"[CHROMADB SEARCH ERROR] {str(e)}")
            return {
                "success": False,
                "chunks": [],
                "count": 0,
                "error": str(e)
            }
    
    async def _check_relevance(self, query: str, chromadb_result: Dict) -> Dict[str, Any]:
        """Thought: Check if ChromaDB results are truly relevant"""
        chunks = chromadb_result.get("chunks", [])
        
        if not chunks:
            return {
                "is_relevant": False,
                "verdict": "NO_RESULTS",
                "reason": "No chunks found in ChromaDB",
                "score": 0.0
            }
        
        # Get top 3 chunks for verification
        top_chunks = chunks[:3]
        context_text = "\n\n".join([
            f"Chunk {i+1}: {chunk['document'][:300]}"
            for i, chunk in enumerate(top_chunks)
        ])
        
        # Ask LLM to verify relevance
        verification_prompt = f"""You are a relevance checker. Determine if these text chunks can answer the user's question.

Question: {query}

Retrieved Text Chunks:
{context_text}

Instructions:
Respond ONLY with one of these formats:

RELEVANT - [brief reason]
NOT_RELEVANT - [brief reason]

Examples:
RELEVANT - Chunks discuss AIR University admissions directly
NOT_RELEVANT - Chunks are about Bahria University, not AIR University

Now analyze:"""

        try:
            llm_response = await self.llm_service.generate(
                prompt=verification_prompt,
                temperature=0.1,
                max_tokens=100
            )
            
            response_lower = llm_response.lower()
            is_relevant = "relevant" in response_lower and "not_relevant" not in response_lower
            
            # Extract reason
            if " - " in llm_response:
                reason = llm_response.split(" - ", 1)[1].strip()
            else:
                reason = "LLM verification completed"
            
            # Calculate score from ChromaDB results
            scores = [chunk.get("score", 0.0) for chunk in chunks]
            max_score = max(scores) if scores else 0.0
            
            verdict = "RELEVANT" if is_relevant else "NOT_RELEVANT"
            
            return {
                "is_relevant": is_relevant,
                "verdict": verdict,
                "reason": reason,
                "score": max_score,
                "llm_response": llm_response
            }
        
        except Exception as e:
            logger.error(f"[RELEVANCE CHECK ERROR] {str(e)}")
            # Conservative: assume relevant if check fails
            return {
                "is_relevant": True,
                "verdict": "CHECK_FAILED",
                "reason": f"Verification failed: {str(e)}",
                "score": 0.5
            }
    
    async def _search_internet(self, query: str) -> Dict[str, Any]:
        """Action: Search internet using Tavily AI"""
        try:
            from tavily import TavilyClient
            import os
            
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                logger.warning("[TAVILY] API key not found, skipping internet search")
                return {"success": False, "results": [], "error": "API key missing"}
            
            logger.info(f"[TAVILY] Searching for: {query}")
            
            client = TavilyClient(api_key=tavily_api_key)
            
            response = client.search(
                query=query,
                search_depth="advanced",  # "basic" or "advanced"
                max_results=5,
                include_answer=False,  # We'll generate our own with LLM
                include_raw_content=False,
                include_images=False
            )
            
            # Parse results
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("content", ""),
                    "url": result.get("url", ""),
                    "source": result.get("url", "").split("/")[2] if result.get("url") else "Unknown",
                    "score": result.get("score", 0.0)
                })
            
            logger.info(f"[TAVILY] ✅ Found {len(results)} results")
            
            return {
                "success": True,
                "results": results,
                "query": query
            }
        
        except Exception as e:
            logger.error(f"[TAVILY ERROR] {str(e)}", exc_info=True)
            return {
                "success": False,
                "results": [],
                "error": str(e)
            }
    
    async def _generate_answer_from_chromadb(
        self, 
        query: str, 
        chromadb_result: Dict
    ) -> str:
        """Action: Generate answer from ChromaDB chunks"""
        chunks = chromadb_result.get("chunks", [])
        
        context_text = "\n\n".join([
            f"[Source {i+1}]: {chunk['document']}"
            for i, chunk in enumerate(chunks[:3])
        ])
        
        system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.

Instructions:
1. Use ONLY the information from the provided context
2. Be accurate and cite sources when relevant
3. If context doesn't fully answer the question, say so
4. Be concise but comprehensive"""
        
        user_prompt = f"""Context from uploaded documents:
{context_text}

Question: {query}

Provide a detailed answer based on the context above:"""
        
        answer = await self.llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Add source attribution
        sources = list(set([
            chunk.get("metadata", {}).get("source", "Unknown")
            for chunk in chunks[:3]
        ]))
        
        footer = f"\n\n---\n✅ **Source**: Your Uploaded Documents ({', '.join(sources[:2])})"
        
        return f"{answer}{footer}"
    
    async def _generate_answer_from_internet(
        self, 
        query: str, 
        internet_result: Dict
    ) -> str:
        """Action: Generate answer from internet sources"""
        results = internet_result.get("results", [])
        
        if not results:
            return await self._generate_answer_from_knowledge(query)
        
        # Format internet results for LLM
        context_parts = []
        for i, result in enumerate(results[:5], 1):
            context_parts.append(f"""[Source {i}: {result['title']}]
URL: {result['url']}
Content: {result['snippet']}
""")
        
        context_text = "\n\n".join(context_parts)
        
        system_prompt = """You are a helpful AI assistant that provides accurate answers based on internet search results.

Instructions:
1. Analyze the search results carefully
2. Extract key information relevant to the question
3. Synthesize a clear, comprehensive answer
4. Cite sources when making claims
5. If results are insufficient, supplement with your knowledge but indicate this"""
        
        user_prompt = f"""Internet search results:

{context_text}

Question: {query}

Provide a comprehensive answer based on these search results:"""
        
        answer = await self.llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Add source attribution
        sources = list(set([r.get("source", "Internet") for r in results[:3]]))
        footer = f"\n\n---\n🌐 **Source**: Internet Search Results\n📚 **Based on**: {', '.join(sources)}"
        
        return f"{answer}{footer}"
    
    async def _generate_answer_from_knowledge(self, query: str) -> str:
        """Action: Generate answer from LLM's general knowledge"""
        system_prompt = """You are a knowledgeable AI assistant with expertise across many domains.

IMPORTANT INSTRUCTIONS:
- Answer questions directly and confidently
- NEVER start with disclaimers like "I don't have", "I couldn't find"
- If you have knowledge about the topic, share it immediately
- Be factual, comprehensive, and helpful
- Organize information clearly with relevant details"""
        
        user_prompt = f"""Question: {query}

Provide a comprehensive, informative answer based on your general knowledge:"""
        
        answer = await self.llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Clean up hedging phrases
        answer = self._clean_response(answer)
        
        footer = "\n\n---\nℹ️ **Source**: General AI Knowledge (no relevant documents or internet results found)"
        
        return f"{answer}{footer}"
    
    def _clean_response(self, answer: str) -> str:
        """Remove hedging phrases from responses"""
        import re
        
        hedging_patterns = [
            r"^I couldn't find (much |any )?information about.*?\.(\s*However,?)?\s*",
            r"^I don't have (much |any )?information about.*?\.(\s*However,?)?\s*",
            r"^I wasn't able to find.*?\.(\s*However,?)?\s*",
        ]
        
        cleaned = answer
        for pattern in hedging_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned)
        cleaned = re.sub(r'  +', ' ', cleaned)
        
        return cleaned.strip()
    
    def _build_response(
        self,
        answer: str,
        source: str,
        chunks: List[Dict],
        relevance_score: float = 0.0,
        internet_sources: List[Dict] = None
    ) -> Dict[str, Any]:
        """Build final response with execution trace"""
        return {
            "answer": answer,
            "source": source,
            "retrieved_chunks": [
                {
                    "content": chunk["document"][:200] + "...",
                    "metadata": chunk.get("metadata", {}),
                    "score": chunk.get("score", 0.0)
                }
                for chunk in chunks
            ],
            "confidence": relevance_score if chunks else 0.7,
            "execution_steps": self.execution_steps,
            "internet_sources": internet_sources or [],
            "agent_type": "coordinator_react"
        }
    
    def _log_step(self, step_type: str, content: str):
        """Log execution step for transparency"""
        step = {
            "type": step_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_steps.append(step)
        
        # Visual logging
        emoji_map = {
            "THOUGHT": "🧠",
            "ACTION": "⚡",
            "OBSERVATION": "👁️",
            "ERROR": "❌"
        }
        
        emoji = emoji_map.get(step_type, "📝")
        logger.info(f"{emoji} [{step_type}] {content}")