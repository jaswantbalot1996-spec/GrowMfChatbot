"""
Semantic Chunking Service
Breaks down scraped Groww AMC pages into meaningful chunks (300-500 tokens) 
optimized for RAG retrieval with full metadata attachment.

Reference: CHUNKING_STRATEGY.md
"""

import hashlib
import logging
import re
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from transformers import AutoTokenizer
import nltk
from .config import ChunkingConfig

# Download NLTK tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)
logger.setLevel(ChunkingConfig.LOG_LEVEL)


class ChunkingService:
    """Service for semantic chunking of Groww AMC pages"""
    
    def __init__(self):
        """Initialize chunking service with tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            ChunkingConfig.TOKENIZER_MODEL
        )
        self.min_tokens = ChunkingConfig.MIN_TOKENS
        self.max_tokens = ChunkingConfig.MAX_TOKENS
        self.overlap_tokens = ChunkingConfig.OVERLAP_TOKENS
        logger.info(f"ChunkingService initialized: {self.min_tokens}-{self.max_tokens} tokens")
    
    def preprocess_html(self, raw_html: str) -> str:
        """
        Remove boilerplate, normalize text, extract main content.
        
        Args:
            raw_html: Raw HTML from scraped page
            
        Returns:
            Cleaned text ready for chunking
        """
        logger.debug("Preprocessing HTML")
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove boilerplate elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'noscript', 'header']):
            tag.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Normalize unicode (handle currency symbols, special chars)
        text = unicodedata.normalize('NFKD', text)
        
        # Remove URLs and email addresses
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences using NLTK.
        
        Args:
            text: Cleaned text
            
        Returns:
            List of sentences
        """
        try:
            sentences = nltk.sent_tokenize(text)
        except Exception as e:
            logger.warning(f"NLTK tokenization failed: {e}. Using regex fallback.")
            # Fallback: split on period, exclamation, question mark
            sentences = re.split(r'[.!?]+', text)
        
        # Filter out very short "sentences"
        sentences = [
            s.strip() for s in sentences 
            if len(s.split()) > ChunkingConfig.MIN_SENTENCE_LENGTH_WORDS
        ]
        
        logger.debug(f"Split into {len(sentences)} sentences")
        return sentences
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tokenizer"""
        return len(self.tokenizer.encode(text))
    
    def tokenize_and_chunk(self, sentences: List[str]) -> List[Dict[str, any]]:
        """
        Greedily combine sentences into chunks (min_tokens to max_tokens).
        Implements sliding window with overlap.
        
        Args:
            sentences: List of sentences from text segmentation
            
        Returns:
            List of chunk dicts with text and token_count
        """
        logger.debug(f"Tokenizing and chunking {len(sentences)} sentences")
        
        # Pre-tokenize sentences for efficiency
        sentence_tokens = [self._count_tokens(s) for s in sentences]
        
        chunks = []
        i = 0
        chunk_counter = 0
        
        while i < len(sentences):
            chunk_sentences = []
            chunk_tokens = 0
            start_idx = i
            
            # Greedily add sentences until max_tokens
            while i < len(sentences) and chunk_tokens < self.max_tokens:
                tokens = sentence_tokens[i]
                
                if chunk_tokens + tokens <= self.max_tokens:
                    chunk_sentences.append(sentences[i])
                    chunk_tokens += tokens
                    i += 1
                else:
                    break
            
            # Only yield chunk if it meets minimum token requirement
            if chunk_tokens >= self.min_tokens:
                chunk_text = ' '.join(chunk_sentences)
                chunks.append({
                    'text': chunk_text,
                    'token_count': chunk_tokens,
                    'sentence_range': (start_idx, i - 1),
                })
                chunk_counter += 1
            
            # Backtrack for overlap (reuse last ~50 tokens / ~10% of chunk)
            overlap_sentences = max(0, self.overlap_tokens // 50)
            i = max(start_idx + 1, i - overlap_sentences)
        
        logger.info(f"Created {chunk_counter} chunks from {len(sentences)} sentences")
        return chunks
    
    def extract_concepts(self, chunk_text: str) -> List[str]:
        """
        Extract concept tags from chunk using regex patterns.
        
        Args:
            chunk_text: Text of the chunk
            
        Returns:
            List of concept tags (expense_ratio, exit_load, etc.)
        """
        concepts = []
        
        for concept, pattern in ChunkingConfig.CONCEPT_PATTERNS.items():
            if re.search(pattern, chunk_text, re.IGNORECASE):
                concepts.append(concept)
        
        return concepts
    
    def infer_question_types(self, concepts: List[str]) -> List[str]:
        """
        Infer common question types from concepts.
        
        Args:
            concepts: List of extracted concepts
            
        Returns:
            List of inferred question types
        """
        question_map = {
            'expense_ratio': 'what_is_expense_ratio',
            'exit_load': 'what_is_exit_load',
            'lock_in': 'what_is_lock_in_period',
            'minimum_sip': 'what_is_minimum_sip',
            'statement': 'how_to_download_statement',
            'riskometer': 'what_is_riskometer',
            'fund_details': 'fund_information',
        }
        
        question_types = [
            question_map[concept] 
            for concept in concepts 
            if concept in question_map
        ]
        
        return question_types
    
    def add_metadata(self,
                     chunk: Dict,
                     source_url: str,
                     amc_name: str,
                     scheme_info: Dict,
                     scraped_datetime: str,
                     chunk_idx: int) -> Dict:
        """
        Attach full metadata to chunk.
        
        Args:
            chunk: Chunk dict with text and token_count
            source_url: Source URL (Groww AMC page)
            amc_name: AMC name (HDFC, ICICI, etc.)
            scheme_info: {'name': str, 'isin': str, ...}
            scraped_datetime: ISO 8601 timestamp
            chunk_idx: Index of chunk for this AMC/scheme combo
            
        Returns:
            Enriched chunk dict with metadata
        """
        concepts = self.extract_concepts(chunk['text'])
        
        chunk_id = f"{amc_name}_{scheme_info.get('name', 'unknown').lower()}_{chunk_idx:03d}"
        
        return {
            'chunk_id': chunk_id,
            'text': chunk['text'],
            'token_count': chunk['token_count'],
            'source_url': source_url,
            'amc_name': amc_name,
            'scheme_name': scheme_info.get('name', 'Unknown Scheme'),
            'scheme_isin': scheme_info.get('isin', 'N/A'),
            'document_type': 'scheme_page',
            'concepts': concepts,
            'question_types': self.infer_question_types(concepts),
            'scraped_datetime': scraped_datetime,
            'last_verified_date': scraped_datetime.split('T')[0],
            'content_hash': hashlib.sha256(chunk['text'].encode()).hexdigest(),
            'embedding': None,  # Filled during embedding phase
            'confidence_score': 0.9,
            'metadata': {
                'sentence_range': chunk.get('sentence_range'),
                'related_schemes': [],
            }
        }
    
    def chunk_groww_amc_page(self,
                            raw_html: str,
                            source_url: str,
                            amc_name: str,
                            scraped_datetime: str,
                            scheme_info: Optional[Dict] = None) -> List[Dict]:
        """
        Main entry point: HTML → Chunks with full metadata.
        
        Args:
            raw_html: Raw HTML from scraped Groww page
            source_url: Source URL
            amc_name: AMC name
            scraped_datetime: ISO 8601 timestamp
            scheme_info: Optional scheme metadata {name, isin, category, ...}
            
        Returns:
            List of chunks with full metadata
        """
        if scheme_info is None:
            scheme_info = {'name': amc_name, 'isin': 'N/A'}
        
        logger.info(f"Chunking {amc_name} from {source_url}")
        
        # Step 1: Preprocess
        clean_text = self.preprocess_html(raw_html)
        
        # Step 2: Sentence segmentation
        sentences = self.split_into_sentences(clean_text)
        
        # Step 3: Tokenize and chunk
        chunks = self.tokenize_and_chunk(sentences)
        
        # Step 4: Attach metadata
        enriched_chunks = []
        for idx, chunk in enumerate(chunks):
            enriched = self.add_metadata(
                chunk,
                source_url=source_url,
                amc_name=amc_name,
                scheme_info=scheme_info,
                scraped_datetime=scraped_datetime,
                chunk_idx=idx
            )
            enriched_chunks.append(enriched)
        
        logger.info(f"Created {len(enriched_chunks)} chunks for {amc_name}")
        return enriched_chunks
    
    def chunk_batch(self, html_batch: List[Dict]) -> List[Dict]:
        """
        Process multiple pages in batch.
        
        Args:
            html_batch: List of {raw_html, source_url, amc_name, scraped_datetime, scheme_info}
            
        Returns:
            Flat list of all chunks
        """
        all_chunks = []
        
        for item in html_batch:
            chunks = self.chunk_groww_amc_page(
                raw_html=item['raw_html'],
                source_url=item['source_url'],
                amc_name=item['amc_name'],
                scraped_datetime=item['scraped_datetime'],
                scheme_info=item.get('scheme_info'),
            )
            all_chunks.extend(chunks)
        
        logger.info(f"Batch processing complete: {len(all_chunks)} total chunks")
        return all_chunks
    
    @staticmethod
    def validate_chunks(chunks: List[Dict]) -> Dict:
        """
        Validate chunking quality.
        
        Returns:
            Dict with stats and warnings
        """
        if not chunks:
            return {'stats': {}, 'warnings': ['No chunks to validate']}
        
        token_counts = [c['token_count'] for c in chunks]
        
        stats = {
            'total_chunks': len(chunks),
            'avg_tokens': sum(token_counts) / len(chunks),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'below_min': sum(1 for c in chunks if c['token_count'] < 300),
            'above_max': sum(1 for c in chunks if c['token_count'] > 500),
            'with_concepts': sum(1 for c in chunks if len(c.get('concepts', [])) > 0),
        }
        
        warnings = []
        if stats['below_min'] > 0:
            warnings.append(f"{stats['below_min']} chunks below 300 tokens")
        if stats['above_max'] > 0:
            warnings.append(f"{stats['above_max']} chunks above 500 tokens")
        if stats['with_concepts'] < len(chunks) * 0.8:
            warnings.append("Many chunks lack concept tags")
        
        return {'stats': stats, 'warnings': warnings}
