from flask import Flask, render_template, request, jsonify, url_for
from pathlib import Path
import json
import numpy as np

try:
    import faiss
except Exception:
    raise RuntimeError('faiss is required for the webapp')

from sentence_transformers import SentenceTransformer


def create_app(index_dir: str = 'indexes', model_name: str = 'all-MiniLM-L6-v2'):
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / 'templates'),
        static_folder=str(Path(__file__).parent.parent / 'static'),
    )

    # Load index and metadata once at startup
    idx_path = Path(index_dir) / 'faiss_index.index'
    meta_path = Path(index_dir) / 'metadata.jsonl'
    if not idx_path.exists() or not meta_path.exists():
        raise RuntimeError(f'Index or metadata not found in {index_dir}')

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


    @app.route('/', methods=['GET'])
    def index():
        return render_template('search.html')


    @app.route('/search', methods=['POST'])
    def search():
        # Keep the classic form endpoint for non-JS fallback; delegate to API
        q = request.form.get('q', '').strip()
        if not q:
            return render_template('search.html', error='Please enter a query')
        # Fixed settings: top_k and threshold are not chosen by the user in the UI
        top_k = 50
        threshold = 0.5

        # call the same logic as the API
        q_emb = model.encode([q], convert_to_numpy=True)
        if q_emb.dtype != np.float32:
            q_emb = q_emb.astype('float32')
        q_emb = l2_normalize(q_emb, axis=1)

        D, I = faiss_index.search(q_emb, top_k)
        D = D[0]
        I = I[0]

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

        return render_template('search.html', query=q, results=results)


    @app.route('/api/search', methods=['GET', 'POST'])
    def api_search():
        # Accept JSON body or query params
        if request.method == 'POST' and request.is_json:
            payload = request.get_json()
            q = (payload.get('q') or '').strip()
            # ignore client-provided values; enforce fixed settings
            top_k = 50
            threshold = 0.5
        else:
            q = (request.args.get('q') or '').strip()
            top_k = 50
            threshold = 0.5

        if not q:
            return jsonify({'error': 'empty query', 'results': []}), 400

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


    return app


if __name__ == '__main__':
    # simple local run
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
