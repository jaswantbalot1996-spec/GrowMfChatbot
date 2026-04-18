"""
Query Handler and FastAPI Application
Implements query validation, retrieval, and response generation.

Reference: RAG_ARCHITECTURE.md sections 4-7
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import QueryAPIConfig

logger = logging.getLogger(__name__)
logger.setLevel(QueryAPIConfig.LOG_LEVEL)


# ============================================================================
# Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    """Input query request"""
    query: str
    top_k: Optional[int] = QueryAPIConfig.TOP_K_RESULTS


class RetrievedChunk(BaseModel):
    """Retrieved chunk in response"""
    chunk_id: str
    text: str
    score: float
    amc_name: str
    scheme_name: str
    source_url: str


class QueryResponse(BaseModel):
    """Query response with answer and citations"""
    query: str
    answer: str
    source_url: str
    source_amc: str
    source_scheme: str
    last_updated: str
    retrieved_chunks: List[RetrievedChunk]
    response_time_ms: float
    confidence_score: float


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    query: str
    suggestion: str


# ============================================================================
# Input Validation & PII Detection
# ============================================================================

class InputValidator:
    """Validate and sanitize user input"""
    
    # PII patterns
    PAN_PATTERN = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'  # Indian PAN format
    AADHAAR_PATTERN = r'\b\d{12}\b'  # Aadhaar: 12 digits
    PHONE_PATTERN = r'\b\d{10}\b'  # Indian phone: 10 digits
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    OTP_PATTERN = r'\b(otp|OTP|one.?time|verification code)\b'
    
    # Advice patterns
    ADVICE_PATTERNS = [
        r'\bshould\s+(i|we|one)',
        r'\b(best|right|suitable)\s+(for|to)',
        r'\bwill\s+(i\s+)?earn',
        r'\b(predict|predict|forecast)',
        r'\b(safe|risky)\s+(now|at this time)',
        r'\b(buy|sell|invest|switch|redeem)',
    ]
    
    @staticmethod
    def detect_pii(query: str) -> List[str]:
        """Detect PII in query"""
        issues = []
        
        if re.search(InputValidator.PAN_PATTERN, query):
            issues.append('PAN')
        if re.search(InputValidator.AADHAAR_PATTERN, query):
            issues.append('Aadhaar')
        if re.search(InputValidator.PHONE_PATTERN, query):
            issues.append('phone number')
        if re.search(InputValidator.EMAIL_PATTERN, query):
            issues.append('email address')
        if re.search(InputValidator.OTP_PATTERN, query):
            issues.append('OTP/password')
        
        return issues
    
    @staticmethod
    def detect_advice_request(query: str) -> bool:
        """Check if query is asking for investment advice"""
        for pattern in InputValidator.ADVICE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate query and return (is_valid, error_message).
        
        Args:
            query: User query
            
        Returns:
            (is_valid, error_message)
        """
        # Check length
        if len(query) > QueryAPIConfig.MAX_QUERY_LENGTH:
            return False, f"Query too long (max {QueryAPIConfig.MAX_QUERY_LENGTH} chars)"
        
        if len(query.strip()) < 5:
            return False, "Query too short (min 5 chars)"
        
        # Check for PII
        pii_found = InputValidator.detect_pii(query)
        if pii_found:
            return False, f"Detected personal info: {', '.join(pii_found)}"
        
        return True, None


# ============================================================================
# Query Classification
# ============================================================================

class QueryClassifier:
    """Classify query intent"""
    
    INTENT_FACTUAL = 'factual'
    INTENT_ADVICE = 'advice'
    INTENT_OUT_OF_SCOPE = 'out_of_scope'
    
    FACTUAL_KEYWORDS = [
        'what', 'when', 'where', 'how much', 'expense', 'exit load',
        'lock', 'sip', 'minimum', 'isin', 'aum', 'riskometer'
    ]
    
    @staticmethod
    def classify(query: str) -> str:
        """
        Classify query intent.
        
        Returns:
            One of: factual, advice, out_of_scope
        """
        query_lower = query.lower()
        
        # Check for advice keywords
        if InputValidator.detect_advice_request(query):
            return QueryClassifier.INTENT_ADVICE
        
        # Check for factual keywords
        for keyword in QueryClassifier.FACTUAL_KEYWORDS:
            if keyword in query_lower:
                return QueryClassifier.INTENT_FACTUAL
        
        # Default
        if any(word in query_lower for word in ['tell', 'explain', 'describe', 'info']):
            return QueryClassifier.INTENT_FACTUAL
        
        return QueryClassifier.INTENT_OUT_OF_SCOPE


# ============================================================================
# Response Templates
# ============================================================================

class ResponseTemplates:
    """Response templates for different query types"""
    
    @staticmethod
    def pii_detected(pii_types: List[str]) -> ErrorResponse:
        """Response when PII detected"""
        return ErrorResponse(
            error="Cannot process personal information",
            query="",
            suggestion=f"I cannot store or process {', '.join(pii_types)}. For account-specific support, contact Groww Help.",
        )
    
    @staticmethod
    def advice_query() -> ErrorResponse:
        """Response for investment advice requests"""
        return ErrorResponse(
            error="Cannot provide investment advice",
            query="",
            suggestion="I only provide factual information, not investment advice. For personalized guidance, consult a financial advisor.",
        )
    
    @staticmethod
    def no_results() -> ErrorResponse:
        """Response when no matching chunks found"""
        return ErrorResponse(
            error="Information not found",
            query="",
            suggestion="I couldn't find reliable information about this in official Groww sources. Try asking about: expense ratios, exit loads, lock-in periods, ELSS, riskometer, minimum SIP, or ISIN.",
        )
    
    @staticmethod
    def out_of_scope() -> ErrorResponse:
        """Response for out-of-scope queries"""
        return ErrorResponse(
            error="Out of scope",
            query="",
            suggestion="I can help with factual questions about Groww mutual funds (expense ratios, exit loads, lock-ins, etc.). What would you like to know?",
        )


# ============================================================================
# Query Handler
# ============================================================================

class QueryHandler:
    """Main query handler orchestrating validation, retrieval, generation"""
    
    def __init__(self,
                 hybrid_retriever,
                 embedding_service,
                 llm_client):
        """
        Initialize handler.
        
        Args:
            hybrid_retriever: HybridRetriever instance
            embedding_service: EmbeddingService instance
            llm_client: LLM client (OpenAI, Anthropic, etc.)
        """
        self.retriever = hybrid_retriever
        self.embedding_service = embedding_service
        self.llm = llm_client
        logger.info("QueryHandler initialized")
    
    def handle_query(self, query: str, top_k: int = 5) -> Dict:
        """
        Process user query.
        
        Args:
            query: User query
            top_k: Top-K results
            
        Returns:
            Dict with answer and metadata
        """
        start_time = time.time()
        
        logger.info(f"Processing query: {query[:50]}...")
        
        # Step 1: Validate input
        is_valid, error_msg = InputValidator.validate_query(query)
        if not is_valid:
            logger.warning(f"Query validation failed: {error_msg}")
            return {'error': error_msg}
        
        # Step 2: Check for PII
        pii_found = InputValidator.detect_pii(query)
        if pii_found:
            logger.warning(f"PII detected in query: {pii_found}")
            return {
                'error': 'pii_detected',
                'message': f"Cannot process: {', '.join(pii_found)}"
            }
        
        # Step 3: Classify query
        intent = QueryClassifier.classify(query)
        logger.debug(f"Query intent: {intent}")
        
        if intent == QueryClassifier.INTENT_ADVICE:
            return {'error': 'advice_query'}
        
        if intent == QueryClassifier.INTENT_OUT_OF_SCOPE:
            return {'error': 'out_of_scope'}
        
        # Step 4: Embed query
        try:
            query_embedding = self.embedding_service.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            return {'error': 'embedding_failed'}
        
        # Step 5: Retrieve
        try:
            retrieved = self.retriever.retrieve(
                query_embedding,
                query,
                top_k=top_k
            )
        except Exception as e:
            logger.error(f"Failed to retrieve: {e}")
            return {'error': 'retrieval_failed'}
        
        if not retrieved:
            logger.warning("No chunks retrieved")
            return {'error': 'no_results'}
        
        # Filter by minimum score
        retrieved = [
            r for r in retrieved
            if r.get('fused_score', 0) >= QueryAPIConfig.MIN_SIMILARITY_SCORE
        ]
        
        if not retrieved:
            logger.warning("No chunks above threshold")
            return {'error': 'low_confidence'}
        
        # Step 6: Extract source chunks for context assembly
        context_chunks = retrieved[:3]  # Top-3 for context
        source_chunk = retrieved[0]  # Primary source
        
        # Step 7: Generate response (via LLM)
        try:
            response = self._generate_response(query, context_chunks)
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {'error': 'generation_failed'}
        
        elapsed = (time.time() - start_time) * 1000  # ms
        
        logger.info(f"Query processed in {elapsed:.1f}ms")
        
        return {
            'success': True,
            'query': query,
            'answer': response['answer'],
            'source_url': source_chunk['metadata'].get('source_url', ''),
            'source_amc': source_chunk['metadata'].get('amc_name', ''),
            'source_scheme': source_chunk['metadata'].get('scheme_name', ''),
            'last_updated': datetime.now().isoformat().split('T')[0],
            'retrieved_chunks': [
                {
                    'chunk_id': r['chunk_id'],
                    'score': r['fused_score'],
                    'amc_name': r['metadata'].get('amc_name', ''),
                    'scheme_name': r['metadata'].get('scheme_name', ''),
                    'source_url': r['metadata'].get('source_url', ''),
                }
                for r in retrieved
            ],
            'response_time_ms': elapsed,
            'confidence_score': float(source_chunk['fused_score']),
        }
    
    def _generate_response(self, query: str, context_chunks: List[Dict]) -> Dict:
        """
        Generate LLM response from context.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            
        Returns:
            Dict with answer
        """
        # Assemble context
        context_text = "\n\n".join([
            f"[Chunk {i+1}] {c.get('chunk_id', '')}\n{c.get('text', '')}"
            for i, c in enumerate(context_chunks)
        ])
        
        # Build prompt
        prompt = f"""You are a factual FAQ assistant for Groww mutual funds.
Answer factual questions ONLY based on provided sources.
Respond in ≤3 sentences. Include source URL.

RULES:
- NO investment advice or portfolio recommendations
- NO performance comparisons or returns computation
- Include timestamp: "Last updated: YYYY-MM-DD"
- Cite exactly ONE source URL
- Refuse personal info requests

QUESTION: {query}

CONTEXT:
{context_text}

ANSWER:"""
        
        # Call LLM (stub implementation)
        # In real implementation, call GPT-4 / Claude 3.5 / Llama 2
        answer = "This is a stub LLM response. Replace with actual LLM call."
        
        return {'answer': answer}


# ============================================================================
# FastAPI Application
# ============================================================================

def create_app(hybrid_retriever, embedding_service, llm_client) -> FastAPI:
    """
    Create FastAPI application.
    
    Args:
        hybrid_retriever: HybridRetriever instance
        embedding_service: EmbeddingService instance
        llm_client: LLM client
        
    Returns:
        FastAPI app
    """
    app = FastAPI(
        title="Groww Mutual Fund FAQ API",
        description="RAG-based FAQ system for Groww mutual funds",
        version="2.0.0",
    )
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    # Initialize handler
    handler = QueryHandler(hybrid_retriever, embedding_service, llm_client)
    
    # Routes
    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "ok", "timestamp": datetime.now().isoformat()}
    
    @app.post("/query", response_model=QueryResponse)
    async def query_endpoint(request: QueryRequest):
        """Query endpoint"""
        logger.info(f"Query endpoint called")
        
        result = handler.handle_query(request.query, request.top_k)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result)
        
        return QueryResponse(**result)
    
    @app.get("/config")
    def get_config():
        """Get API configuration"""
        return QueryAPIConfig.to_dict()
    
    return app
