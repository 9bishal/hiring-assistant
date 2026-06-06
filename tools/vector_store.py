"""
tools/vector_store.py
=====================
ChromaDB vector store for semantic resume retrieval.

IMPRESSIVE FEATURE FOR 10-12 LPA:
  Instead of just keyword matching resumes against the JD,
  we embed both the JD and each resume into a vector space
  and use COSINE SIMILARITY to find the best semantic matches.

  This means "developed ML models" and "built machine learning
  pipelines" are recognized as similar — keyword search misses this.

How to explain to HR:
  "I store all uploaded resumes as vector embeddings in ChromaDB.
   When screening, I do a semantic similarity search against the
   job description embedding. This catches candidates who used
   different wording for the same skills — something pure keyword
   matching completely misses. It's the same retrieval technique
   used in RAG systems."
"""

import chromadb
from chromadb.utils import embedding_functions


# ── ChromaDB Client (in-memory for demo; use persistent for prod) ─────────────
_client = chromadb.Client()   # use chromadb.PersistentClient(path="./chroma_db") for prod

# ── Embedding function — uses sentence-transformers (free, local) ──────────────
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"    # small, fast, good quality
)


def get_or_create_collection(session_id: str):
    """Get or create a ChromaDB collection for this session."""
    name = f"resumes_{session_id}"
    try:
        return _client.get_collection(name=name, embedding_function=_embed_fn)
    except Exception:
        return _client.create_collection(name=name, embedding_function=_embed_fn)


def store_resumes(session_id: str, names: list[str], texts: list[str]):
    """
    Store all resumes as vector embeddings in ChromaDB.

    Args:
        session_id: unique ID for this hiring session
        names:      list of filenames
        texts:      list of parsed resume texts
    """
    collection = get_or_create_collection(session_id)

    # Clear any previous data for this session
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # Add each resume
    collection.add(
        ids        = [f"resume_{i}" for i in range(len(names))],
        documents  = texts,
        metadatas  = [{"name": name} for name in names],
    )


def semantic_search(session_id: str, query: str, top_k: int = 5) -> list[dict]:
    """
    Find the most semantically similar resumes to a query (e.g. the JD).

    Returns:
        List of { name, text, similarity_score } sorted by relevance
    """
    collection = get_or_create_collection(session_id)
    results    = collection.query(query_texts=[query], n_results=top_k)

    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "name":  results["metadatas"][0][i]["name"],
            "text":  doc,
            "score": round(1 - results["distances"][0][i], 3),  # cosine similarity
        })

    return output


def delete_session(session_id: str):
    """Clean up a session's collection."""
    try:
        _client.delete_collection(f"resumes_{session_id}")
    except Exception:
        pass
