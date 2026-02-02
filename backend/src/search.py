"""search.py

Load FAISS index and metadata then search for semantic nearest neighbors for a query.

Usage examples:
  python -m src.search --query "How to reset my password?"

Output: JSON list of up to top-k results with `id`, `score`, `snippet`, `url`, and `source_file`.
"""
import argparse
import json
from pathlib import Path

import numpy as np

try:
    import faiss
except Exception as e:
    raise RuntimeError("faiss is required. Install faiss-cpu or use conda-forge on Windows.") from e

from sentence_transformers import SentenceTransformer


def load_metadata(meta_path: Path):
    if not meta_path.exists():
        return []
    out = []
    with meta_path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                out.append({'raw': line})
    return out


def l2_normalize(x: np.ndarray, axis: int = 1, eps: float = 1e-12):
    norms = np.linalg.norm(x, axis=axis, keepdims=True)
    norms = np.maximum(norms, eps)
    return x / norms


def main():
    ap = argparse.ArgumentParser(description='Semantic search over FAISS index')
    ap.add_argument('--index-dir', default='indexes', help='Index directory')
    ap.add_argument('--model', default='all-MiniLM-L6-v2', help='SentenceTransformer model')
    ap.add_argument('--query', default=None, help='Query text')
    ap.add_argument('--top-k', type=int, default=5)
    ap.add_argument('--threshold', type=float, default=0.8, help='Cosine similarity threshold (0..1)')
    args = ap.parse_args()

    index_dir = Path(args.index_dir)
    faiss_path = index_dir / 'faiss_index.index'
    meta_path = index_dir / 'metadata.jsonl'

    if not faiss_path.exists():
        print('[search] no index found at', faiss_path)
        return

    # Load index and metadata
    index = faiss.read_index(str(faiss_path))
    metadata = load_metadata(meta_path)

    model = SentenceTransformer(args.model)

    # Read query from CLI or prompt
    q = args.query
    if not q:
        q = input('Query: ').strip()
    if not q:
        print('No query provided')
        return

    q_emb = model.encode([q], convert_to_numpy=True)
    if q_emb.dtype != 'float32':
        q_emb = q_emb.astype('float32')
    q_emb = l2_normalize(q_emb, axis=1)

    k = max(args.top_k, 5)
    D, I = index.search(q_emb, k)
    D = D[0]
    I = I[0]

    results = []
    for score, idx in zip(D, I):
        if idx < 0:
            continue
        # For normalized vectors and IndexFlatIP, inner product == cosine similarity
        cosine = float(score)
        if cosine < args.threshold:
            continue
        meta = metadata[idx] if idx < len(metadata) else {}
        res = {
            'id': meta.get('id'),
            'score': cosine,
            'snippet': meta.get('snippet'),
            'url': meta.get('url'),
            'source_file': meta.get('source_file')
        }
        results.append(res)
        if len(results) >= args.top_k:
            break

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
