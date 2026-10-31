import os
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer


# Project root
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

# Paths
INDEX_PATH = os.path.join(BASE_DIR, "models", "MEMORA_faiss.index")
CHUNKS_PATH = os.path.join(BASE_DIR, "data", "MEMORA_chunks.parquet")


# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load chunk data
chunks_df = pd.read_parquet(CHUNKS_PATH)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def retrieve_documents(query, top_k=5):
    """
    Retrieve the most relevant MEMORA chunks using FAISS.
    """

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for rank, idx in enumerate(indices[0], start=1):

        if idx < 0:
            continue

        results.append({
            "rank": rank,
            "score": float(scores[0][rank - 1]),
            "chunk_id": chunks_df.iloc[idx]["chunk_id"],
            "doc_id": chunks_df.iloc[idx]["doc_id"],
            "source_type": chunks_df.iloc[idx]["source_type"],
            "title": chunks_df.iloc[idx]["title"],
            "content": chunks_df.iloc[idx]["content"]
        })

    return results