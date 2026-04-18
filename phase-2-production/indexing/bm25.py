"""
BM25 Keyword Indexing Service
Enables fast exact-match and wildcard search using Whoosh BM25 index.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class BM25Indexer:
    """BM25 keyword search using Whoosh"""
    
    def __init__(self, index_dir: str = './indexes/bm25'):
        """
        Initialize BM25 indexer.
        
        Args:
            index_dir: Directory for storing index files
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            from whoosh.fields import Schema, TEXT, ID, KEYWORD, DATETIME
            from whoosh.filedb.filestore import FileStorage
            
            self.Schema = Schema
            self.TEXT = TEXT
            self.ID = ID
            self.KEYWORD = KEYWORD
            self.DATETIME = DATETIME
            self.FileStorage = FileStorage
            
            # Define schema
            self.schema = Schema(
                chunk_id=ID(stored=True, unique=True),
                text=TEXT(stored=True),
                amc_name=KEYWORD(stored=True),
                scheme_name=TEXT(stored=True),
                concepts=KEYWORD(stored=True),
                source_url=KEYWORD(stored=True),
            )
            
            self.storage = FileStorage(str(self.index_dir))
            self.ix = None
            self._load_or_create_index()
            
            logger.info(f"BM25 indexer initialized at {self.index_dir}")
            
        except ImportError:
            logger.error("Whoosh not installed. Install with: pip install whoosh")
            self.schema = None
            self.ix = None
        except Exception as e:
            logger.error(f"Failed to initialize BM25 indexer: {e}")
            self.ix = None
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            from whoosh.filedb.filestore import FileStorage
            
            storage = FileStorage(str(self.index_dir))
            
            # Check if index exists
            if storage.index_exists():
                self.ix = storage.open_index()
                logger.info("Loaded existing BM25 index")
            else:
                self.ix = storage.create_index(self.schema)
                logger.info("Created new BM25 index")
        except Exception as e:
            logger.error(f"Failed to load/create index: {e}")
            self.ix = None
    
    def add_chunks(self, chunks: List[Dict], clear_existing: bool = False) -> bool:
        """
        Add chunks to BM25 index.
        
        Args:
            chunks: List of chunk dicts
            clear_existing: If True, clear index before adding
            
        Returns:
            True if successful
        """
        if not self.ix:
            logger.error("BM25 index not initialized")
            return False
        
        if not chunks:
            logger.warning("No chunks to index")
            return True
        
        try:
            writer = self.ix.writer()
            
            # Clear existing if requested
            if clear_existing:
                writer.cancel()  # Cancel current writer
                writer = self.ix.writer(clearexisting=True)
            
            # Add chunks
            for chunk in chunks:
                concepts_str = ','.join(chunk.get('concepts', []))
                
                writer.add_document(
                    chunk_id=chunk.get('chunk_id', ''),
                    text=chunk.get('text', ''),
                    amc_name=chunk.get('amc_name', ''),
                    scheme_name=chunk.get('scheme_name', ''),
                    concepts=concepts_str,
                    source_url=chunk.get('source_url', ''),
                )
            
            writer.commit()
            logger.info(f"Indexed {len(chunks)} chunks in BM25")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index chunks: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for chunks matching query.
        
        Args:
            query: Search query
            top_k: Top-K results
            
        Returns:
            List of matching chunks with scores
        """
        if not self.ix:
            logger.error("BM25 index not initialized")
            return []
        
        try:
            from whoosh.qparser import QueryParser
            
            # Multi-field search
            qp = QueryParser('text', self.ix.schema)
            parsed_query = qp.parse(query)
            
            searcher = self.ix.searcher()
            results = searcher.search(parsed_query, limit=top_k)
            
            matches = []
            for result in results:
                matches.append({
                    'chunk_id': result['chunk_id'],
                    'score': float(result.score),
                    'metadata': {
                        'amc_name': result['amc_name'],
                        'scheme_name': result['scheme_name'],
                        'source_url': result['source_url'],
                        'concepts': result['concepts'],
                    }
                })
            
            searcher.close()
            logger.debug(f"BM25 search found {len(matches)} results")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search BM25 index: {e}")
            return []
    
    def clear_index(self) -> bool:
        """Clear all documents from index"""
        if not self.ix:
            return False
        
        try:
            writer = self.ix.writer(clearexisting=True)
            writer.cancel()
            logger.info("Cleared BM25 index")
            return True
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        if not self.ix:
            return {}
        
        try:
            searcher = self.ix.searcher()
            doc_count = searcher.doc_count_all()
            searcher.close()
            
            return {'total_documents': doc_count}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


class HybridRetriever:
    """Hybrid retrieval combining vector search (semantic) and BM25 (keyword)"""
    
    def __init__(self, vector_db: object, bm25_indexer: BM25Indexer,
                 vector_weight: float = 0.7, keyword_weight: float = 0.3):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_db: Vector database instance (Pinecone or Local)
            bm25_indexer: BM25 keyword indexer
            vector_weight: Weight for vector search scores (default 0.7)
            keyword_weight: Weight for BM25 scores (default 0.3)
        """
        self.vector_db = vector_db
        self.bm25 = bm25_indexer
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # Verify weights sum to 1.0
        assert abs(vector_weight + keyword_weight - 1.0) < 0.01, \
            f"Weights must sum to 1.0 (got {vector_weight + keyword_weight})"
        
        logger.info(f"Hybrid retriever initialized (vector: {vector_weight}, keyword: {keyword_weight})")
    
    def retrieve(self, query_embedding, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Hybrid retrieval: combine vector + keyword search.
        
        Args:
            query_embedding: Query embedding vector
            query_text: Original query text
            top_k: Top-K results
            
        Returns:
            Deduplicated, ranked list of top-K chunks
        """
        logger.debug(f"Hybrid retrieval: top_k={top_k}")
        
        # Vector search (semantic)
        vector_results = self.vector_db.search(query_embedding, top_k=top_k)
        
        # Normalize vector scores (0-1 range)
        if vector_results:
            max_score = max(r['score'] for r in vector_results)
            if max_score > 0:
                for r in vector_results:
                    r['vector_score'] = r['score'] / max_score
            else:
                for r in vector_results:
                    r['vector_score'] = 0.0
        
        # BM25 search (keywords)
        keyword_results = self.bm25.search(query_text, top_k=top_k)
        
        # Normalize BM25 scores
        if keyword_results:
            max_score = max(r['score'] for r in keyword_results)
            if max_score > 0:
                for r in keyword_results:
                    r['keyword_score'] = r['score'] / max_score
            else:
                for r in keyword_results:
                    r['keyword_score'] = 0.0
        
        # Combine results
        combined = {}  # chunk_id -> result
        
        for r in vector_results:
            chunk_id = r['chunk_id']
            combined[chunk_id] = {
                'chunk_id': chunk_id,
                'vector_score': r.get('vector_score', 0.0),
                'keyword_score': 0.0,
                'metadata': r.get('metadata', {}),
            }
        
        for r in keyword_results:
            chunk_id = r['chunk_id']
            if chunk_id in combined:
                combined[chunk_id]['keyword_score'] = r.get('keyword_score', 0.0)
            else:
                combined[chunk_id] = {
                    'chunk_id': chunk_id,
                    'vector_score': 0.0,
                    'keyword_score': r.get('keyword_score', 0.0),
                    'metadata': r.get('metadata', {}),
                }
        
        # Compute fused score
        for chunk_id, result in combined.items():
            result['fused_score'] = (
                self.vector_weight * result['vector_score'] +
                self.keyword_weight * result['keyword_score']
            )
        
        # Rank by fused score
        ranked = sorted(
            combined.values(),
            key=lambda x: x['fused_score'],
            reverse=True
        )[:top_k]
        
        logger.debug(f"Hybrid retrieval returned {len(ranked)} results")
        return ranked
