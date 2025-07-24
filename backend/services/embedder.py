import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from backend.utils.chunking import chunk_text

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIR = "vector_store"
os.makedirs(EMBED_DIR, exist_ok=True)

model = SentenceTransformer(EMBEDDING_MODEL)

def store_document_embeddings(document_id: str, full_text: str):
    chunks = chunk_text(full_text)

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and chunks
    with open(os.path.join(EMBED_DIR, f"{document_id}_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    faiss.write_index(index, os.path.join(EMBED_DIR, f"{document_id}_index.faiss"))

def retrieve_relevant_chunks(document_id: str, query: str, top_k: int = 4):
    query_vec = model.encode([query])

    index_path = os.path.join(EMBED_DIR, f"{document_id}_index.faiss")
    chunks_path = os.path.join(EMBED_DIR, f"{document_id}_chunks.pkl")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError("Embedding index not found for this document")

    index = faiss.read_index(index_path)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    scores, indices = index.search(query_vec, top_k)
    return [chunks[i] for i in indices[0]]
