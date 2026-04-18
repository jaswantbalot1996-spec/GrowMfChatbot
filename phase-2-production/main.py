"""
Phase 2 Orchestrator
Coordinates chunking, embedding, indexing, and query API.

Execution flow:
1. Read raw HTML from Phase-1 scraping (PostgreSQL staging)
2. Chunk content (ChunkingService)
3. Generate embeddings (EmbeddingService)
4. Index in Vector DB + BM25 (PineconeVectorDB, BM25Indexer)
5. Invalidate cache (Redis)
6. Launch query API (FastAPI)

Reference: RAG_ARCHITECTURE.md Section 3
"""

import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add parent to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..' )))

from phase_2_production.chunking.service import ChunkingService
from phase_2_production.chunking.config import ChunkingConfig
from phase_2_production.embedding.service import EmbeddingService, IncrementalEmbeddingUpdater
from phase_2_production.embedding.config import EmbeddingConfig
from phase_2_production.indexing.vectordb import PineconeVectorDB, LocalVectorIndex, get_vector_db
from phase_2_production.indexing.bm25 import BM25Indexer, HybridRetriever
from phase_2_production.query_api.app import create_app
from phase_2_production.query_api.config import QueryAPIConfig

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=QueryAPIConfig.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Phase2Orchestrator:
    """Orchestrates the entire Phase 2 pipeline"""
    
    def __init__(self, use_local_vectordb: bool = False):
        """
        Initialize Phase 2 services.
        
        Args:
            use_local_vectordb: If True, use local in-memory vector DB (testing only)
        """
        logger.info("=" * 80)
        logger.info("PHASE 2: PRODUCTION - Orchestrator Initialization")
        logger.info("=" * 80)
        
        # Initialize services
        logger.info("Initializing ChunkingService...")
        self.chunking_service = ChunkingService()
        
        logger.info("Initializing EmbeddingService...")
        self.embedding_service = EmbeddingService()
        self.embedding_updater = IncrementalEmbeddingUpdater(self.embedding_service)
        
        logger.info("Initializing Vector DB...")
        self.vector_db = get_vector_db(use_local=use_local_vectordb)
        
        logger.info("Initializing BM25 Indexer...")
        self.bm25_indexer = BM25Indexer()
        
        logger.info("Initializing Hybrid Retriever...")
        self.hybrid_retriever = HybridRetriever(
            vector_db=self.vector_db,
            bm25_indexer=self.bm25_indexer,
            vector_weight=0.7,
            keyword_weight=0.3,
        )
        
        logger.info("✓ Phase 2 Orchestrator initialized successfully")
    
    def process_scraped_content(self, html_batch: List[Dict]) -> List[Dict]:
        """
        Process scraped HTML through entire Phase 2 pipeline.
        
        Args:
            html_batch: List of {raw_html, source_url, amc_name, scraped_datetime, scheme_info}
            
        Returns:
            List of processed chunks with embeddings
        """
        logger.info(f"Processing {len(html_batch)} items through Phase 2 pipeline")
        
        # Step 1: Chunk
        logger.info("Step 1: Chunking content...")
        chapters = self.chunking_service.chunk_batch(html_batch)
        logger.info(f"  ✓ Created {len(chapters)} chunks")
        
        # Validate chunks
        validation = ChunkingService.validate_chunks(chapters)
        logger.info(f"  Chunk stats: {validation['stats']}")
        if validation['warnings']:
            for warning in validation['warnings']:
                logger.warning(f"    Warning: {warning}")
        
        # Step 2: Generate embeddings
        logger.info("Step 2: Generating embeddings...")
        embedded_chunks = self.embedding_service.embed_chunks(chapters)
        logger.info(f"  ✓ Embedded {len(embedded_chunks)} chunks")
        
        # Validate embeddings
        from phase_2_production.embedding.service import validate_embeddings
        validate_embeddings(embedded_chunks)
        
        # Step 3: Index in Vector DB
        logger.info("Step 3: Indexing in Vector DB...")
        vector_success = self.vector_db.upsert_embeddings(embedded_chunks)
        if vector_success:
            logger.info(f"  ✓ Upserted {len(embedded_chunks)} embeddings to Vector DB")
        else:
            logger.warning("  ✗ Vector DB indexing may have failed (see logs above)")
        
        # Get Vector DB stats
        try:
            stats = self.vector_db.get_index_stats()
            logger.info(f"  Vector DB stats: {stats}")
        except:
            pass
        
        # Step 4: Index in BM25
        logger.info("Step 4: Indexing in BM25...")
        bm25_success = self.bm25_indexer.add_chunks(embedded_chunks, clear_existing=False)
        if bm25_success:
            logger.info(f"  ✓ Indexed {len(embedded_chunks)} chunks in BM25")
        else:
            logger.warning("  ✗ BM25 indexing may have failed (see logs above)")
        
        # Get BM25 stats
        try:
            stats = self.bm25_indexer.get_index_stats()
            logger.info(f"  BM25 stats: {stats}")
        except:
            pass
        
        logger.info("✓ Phase 2 processing complete")
        return embedded_chunks
    
    def start_query_api(self, host: str = None, port: int = None):
        """
        Start FastAPI query server.
        
        Args:
            host: Server host (defaults to config)
            port: Server port (defaults to config)
        """
        host = host or QueryAPIConfig.HOST
        port = port or QueryAPIConfig.PORT
        
        logger.info(f"Starting Query API on {host}:{port}...")
        
        # Create FastAPI app
        # Note: LLM client is None for now (stub implementation)
        app = create_app(
            hybrid_retriever=self.hybrid_retriever,
            embedding_service=self.embedding_service,
            llm_client=None,  # TODO: Initialize actual LLM client
        )
        
        logger.info(f"✓ FastAPI app created")
        logger.info(f"Query API ready on http://{host}:{port}")
        logger.info(f"  Health check: GET http://{host}:{port}/health")
        logger.info(f"  Query endpoint: POST http://{host}:{port}/query")
        
        return app
    
    def demo_query(self, query: str) -> Dict:
        """
        Demo: Process a test query through the retrieve system.
        
        Args:
            query: Test query
            
        Returns:
            Query result dict
        """
        logger.info(f"Demo query: '{query}'")
        
        # Embed query
        query_embedding = self.embedding_service.embed_query(query)
        
        # Retrieve
        results = self.hybrid_retriever.retrieve(query_embedding, query, top_k=3)
        
        logger.info(f"Retrieved {len(results)} results:")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result['chunk_id']} (score: {result['fused_score']:.4f})")
        
        return {'query': query, 'results': results}


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for Phase 2"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2 Production Pipeline")
    parser.add_argument('--mode', choices=['process', 'api', 'demo'], default='api',
                       help='Execution mode (default: api)')
    parser.add_argument('--local-vectordb', action='store_true',
                       help='Use local in-memory vectordb (testing only)')
    parser.add_argument('--host', default=QueryAPIConfig.HOST)
    parser.add_argument('--port', type=int, default=QueryAPIConfig.PORT)
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = Phase2Orchestrator(use_local_vectordb=args.local_vectordb)
    
    if args.mode == 'api':
        # Start query API
        app = orchestrator.start_query_api(args.host, args.port)
        
        # Import uvicorn and run
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    
    elif args.mode == 'demo':
        # Run demo queries
        demo_queries = [
            "What is the expense ratio of HDFC Large-Cap Fund?",
            "What is the exit load for ELSS?",
            "What is the minimum SIP amount?",
        ]
        
        for query in demo_queries:
            result = orchestrator.demo_query(query)
            logger.info("")
    
    elif args.mode == 'process':
        # Demo processing (would normally read from Phase-1 PostgreSQL)
        logger.info("Demo: Processing sample HTML batch")
        
        sample_batch = [
            {
                'raw_html': '<html><body>HDFC Large-Cap Fund. Expense ratio: 0.50%. Exit load: 1%.</body></html>',
                'source_url': 'https://groww.in/mutual-funds/amc/hdfc-mutual-funds',
                'amc_name': 'HDFC',
                'scraped_datetime': datetime.now().isoformat(),
                'scheme_info': {'name': 'Large-Cap', 'isin': 'INF090A01KX0'},
            }
        ]
        
        chunks = orchestrator.process_scraped_content(sample_batch)
        logger.info(f"Demo processing complete: {len(chunks)} chunks created")


if __name__ == '__main__':
    main()
