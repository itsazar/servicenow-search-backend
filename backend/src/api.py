"""api.py

Flask API server for FAISS semantic search backend.
Handles index loading and serves search results via REST API.
"""
from flask import Flask, jsonify, request
from pathlib import Path
import json
import numpy as np
import os
from dotenv import load_dotenv

try:
    import faiss
except Exception:
    raise RuntimeError('faiss is required for the API backend')

from sentence_transformers import SentenceTransformer


def create_app(index_dir: str = 'indexes', model_name: str = 'all-MiniLM-L6-v2'):
    """Create and configure the Flask API application."""
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # CORS support
    cors_origins = [o.strip() for o in os.getenv('CORS_ORIGINS', '*').split(',')]
    
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in cors_origins or '*' in cors_origins:
            response.headers['Access-Control-Allow-Origin'] = origin if origin else cors_origins[0]
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Load index and metadata once at startup
    # Resolve index directory: if relative, resolve from this file's parent directory
    index_path = Path(index_dir)
    if not index_path.is_absolute():
        index_path = Path(__file__).parent.parent / index_dir
    
    idx_path = index_path / 'faiss_index.index'
    meta_path = index_path / 'metadata.jsonl'
    
    if not idx_path.exists() or not meta_path.exists():
        raise RuntimeError(f'Index or metadata not found in {index_path}. Expected: {idx_path} and {meta_path}')

    faiss_index = faiss.read_index(str(idx_path))
    metadata = []
    with meta_path.open('r', encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                metadata.append(json.loads(line))

    model = SentenceTransformer(model_name)

    def l2_normalize(x: np.ndarray, axis: int = 1, eps: float = 1e-12):
        norms = np.linalg.norm(x, axis=axis, keepdims=True)
        norms = np.maximum(norms, eps)
        return x / norms

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'index_size': len(metadata)})

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        """Search endpoint that accepts query and returns results."""
        # Accept JSON body or query params
        if request.method == 'POST' and request.is_json:
            payload = request.get_json()
            q = (payload.get('q') or '').strip()
            top_k = payload.get('top_k', 50)
            threshold = payload.get('threshold', 0.5)
        else:
            q = (request.args.get('q') or '').strip()
            top_k = request.args.get('top_k', 50, type=int)
            threshold = request.args.get('threshold', 0.5, type=float)

        if not q:
            return jsonify({'error': 'empty query', 'results': []}), 400

        try:
            q_emb = model.encode([q], convert_to_numpy=True)
            if q_emb.dtype != np.float32:
                q_emb = q_emb.astype('float32')
            q_emb = l2_normalize(q_emb, axis=1)

            D, I = faiss_index.search(q_emb, top_k)
            D = D[0].tolist()
            I = I[0].tolist()

            results = []
            for score, idx in zip(D, I):
                if idx < 0:
                    continue
                cosine = float(score)
                if cosine < threshold:
                    continue
                meta = metadata[idx] if idx < len(metadata) else {}
                results.append({
                    'id': meta.get('id'),
                    'thread_id': meta.get('thread_id'),
                    'title': meta.get('title'),
                    'question_text': meta.get('question_text'),
                    'snippet': meta.get('snippet'),
                    'url': meta.get('url'),
                    'score': round(cosine, 4),
                })

            return jsonify({'results': results, 'count': len(results)})
        except Exception as e:
            return jsonify({'error': str(e), 'results': []}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'server error'}), 500

    return app


# Export app instance for production (gunicorn)
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
