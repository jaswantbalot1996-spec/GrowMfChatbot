"""
Flask API Server for Phase 3 - LLM Query Interface
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    raise ImportError("Flask not installed. Install with: pip install flask flask-cors")

from .phase3_service import create_phase3_service
from .config import LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize Phase 3 service (lazy load)
_service = None


def get_service():
    """Get or create Phase 3 service."""
    global _service
    if _service is None:
        logger.info("Initializing Phase 3 service...")
        _service = create_phase3_service()
    return _service


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        service = get_service()
        stats = service.get_statistics()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': stats,
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
        }), 500


@app.route('/query', methods=['POST'])
def query():
    """
    Main query endpoint.
    
    Request body:
    {
        "query": "What is the expense ratio?",
        "top_k": 5  (optional)
    }
    
    Response:
    {
        "query": "What is the expense ratio?",
        "response": "The expense ratio is...",
        "sources": [...],
        "confidence": 0.95,
        "latency_ms": 245.3,
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON body provided'}), 400
        
        query_text = data.get('query', '').strip()
        if not query_text:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        top_k = data.get('top_k')
        
        logger.info(f"Processing query: {query_text[:100]}...")
        
        service = get_service()
        response = service.query(query_text, top_k=top_k)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
        }), 500


@app.route('/batch', methods=['POST'])
def batch_query():
    """
    Batch query endpoint.
    
    Request body:
    {
        "queries": [
            "What is the expense ratio?",
            "Which funds have lowest exit load?"
        ]
    }
    
    Response:
    {
        "responses": [...],
        "count": 2,
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON body provided'}), 400
        
        queries = data.get('queries', [])
        if not queries:
            return jsonify({'error': 'Queries list cannot be empty'}), 400
        
        logger.info(f"Processing batch of {len(queries)} queries...")
        
        service = get_service()
        responses = service.batch_query(queries)
        
        return jsonify({
            'responses': responses,
            'count': len(responses),
            'status': 'success',
        }), 200
        
    except Exception as e:
        logger.error(f"Batch query processing failed: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
        }), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Get service statistics."""
    try:
        service = get_service()
        stats_data = service.get_statistics()
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
        }), 500


@app.route('/info', methods=['GET'])
def info():
    """Get API information."""
    return jsonify({
        'name': 'Groww FAQ API - Phase 3 (Grok + Chroma Cloud)',
        'version': '3.0.0',
        'description': 'LLM-powered FAQ chatbot with hybrid search',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /info': 'API information',
            'GET /stats': 'Service statistics',
            'POST /query': 'Single query',
            'POST /batch': 'Batch queries',
        },
        'features': [
            'Hybrid search (dense + sparse)',
            'Reciprocal Rank Fusion (RRF)',
            'GroupBy deduplication',
            'Grok 2 LLM',
            'Chroma Cloud integration',
        ],
    }), 200


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

def run_server(host: str = "0.0.0.0",
               port: int = 8000,
               debug: bool = False):
    """
    Run the Flask server.
    
    Args:
        host: Server host
        port: Server port
        debug: Debug mode
    """
    logger.info(f"Starting Phase 3 API Server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    debug = '--debug' in sys.argv
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    
    logger.info(f"Phase 3 API Server starting...")
    logger.info(f"  - Host: 0.0.0.0")
    logger.info(f"  - Port: {port}")
    logger.info(f"  - Debug: {debug}")
    logger.info(f"\nEndpoints:")
    logger.info(f"  - Health: GET http://localhost:{port}/health")
    logger.info(f"  - Query:  POST http://localhost:{port}/query")
    logger.info(f"  - Batch:  POST http://localhost:{port}/batch")
    logger.info(f"  - Stats:  GET http://localhost:{port}/stats")
    
    run_server(port=port, debug=debug)
