from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()

EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
DIM = 384
index = faiss.IndexFlatL2(DIM)
doc_chunks = []


def chunk_text(text, max_tokens=200):
    words = text.split()
    chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
    return chunks


def embed_and_store(chunks):
    global doc_chunks
    doc_chunks = chunks
    embeddings = EMBED_MODEL.encode(chunks)
    index.add(np.array(embeddings))

# def embed_and_store(chunks):
#     global doc_chunks, index
#     doc_chunks = chunks
#     embeddings = EMBED_MODEL.encode(chunks)

#     # Reset index on every new upload
#     index = faiss.IndexFlatL2(DIM)
#     index.add(np.array(embeddings))


# def search(query, k=3):
#     query_vec = EMBED_MODEL.encode([query])
#     D, I = index.search(np.array(query_vec), k)
#     return [doc_chunks[i] for i in I[0]]

def search(query, k=3):
    if not doc_chunks or index.ntotal == 0:
        return ["No documents embedded yet. Please upload a document first."]
    
    query_vec = EMBED_MODEL.encode([query])
    D, I = index.search(np.array(query_vec), k)

    # Sanity check: filter out invalid indices
    return [doc_chunks[i] for i in I[0] if i < len(doc_chunks)]


def query_mistral(context, question):
    prompt = f"Answer the following question based on the context.\nContext: {context}\nQuestion: {question}"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://yourappname.onrender.com",  # change as needed
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# def query_mistral(context, question):
#     prompt = f"Answer the following question based on the context.\nContext: {context}\nQuestion: {question}"

#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
#         "HTTP-Referer": "your-app-name", 
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "mistralai/mistral-7b-instruct",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     response = requests.post(url, headers=headers, json=payload)
    
#     try:
#         res_json = response.json()
#         print("Mistral raw response:", res_json)
#         return res_json['choices'][0]['message']['content']
#     except Exception as e:
#         print("Mistral API error:", str(e))
#         print("Response content:", response.text)
#         return "Failed to get a valid response from Mistral."


def is_doc_embedded():
    return len(doc_chunks) > 0 and index.ntotal > 0
