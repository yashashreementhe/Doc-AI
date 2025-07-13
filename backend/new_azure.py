# Root-level project structure and outline

# We will first start by writing the backend files (FastAPI + RAG logic)
# These will go inside the /backend directory.

# File: backend/requirements.txt
# Python dependencies for backend

# fastapi
# uvicorn
# python-multipart
# pydantic
# sentence-transformers
# faiss-cpu
# PyMuPDF
# openpyxl
# requests
# python-dotenv

# ------------------

# File: backend/document_loader.py
# Handles loading of PDF, Excel, TXT

# import fitz  # PyMuPDF
# import openpyxl


# def load_txt(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         return f.read()


# def load_pdf(file_path):
#     doc = fitz.open(file_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text


# def load_excel(file_path):
#     wb = openpyxl.load_workbook(file_path)
#     text = ""
#     for sheet in wb.worksheets:
#         for row in sheet.iter_rows():
#             for cell in row:
#                 if cell.value:
#                     text += str(cell.value) + " "
#     return text


# def extract_text(file_path, extension):
#     if extension == '.txt':
#         return load_txt(file_path)
#     elif extension == '.pdf':
#         return load_pdf(file_path)
#     elif extension in ['.xls', '.xlsx']:
#         return load_excel(file_path)
#     else:
#         raise ValueError("Unsupported file type")

# ------------------

# File: backend/rag_engine.py
# Does chunking, embedding, similarity search, and Mistral querying

# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
# DIM = 384
# index = faiss.IndexFlatL2(DIM)
# doc_chunks = []


# def chunk_text(text, max_tokens=200):
#     words = text.split()
#     chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
#     return chunks


# def embed_and_store(chunks):
#     global doc_chunks
#     doc_chunks = chunks
#     embeddings = EMBED_MODEL.encode(chunks)
#     index.add(np.array(embeddings))


# def search(query, k=3):
#     query_vec = EMBED_MODEL.encode([query])
#     D, I = index.search(np.array(query_vec), k)
#     return [doc_chunks[i] for i in I[0]]


# def query_mistral(context, question):
#     prompt = f"Answer the following question based on the context.\nContext: {context}\nQuestion: {question}"

#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
#         "HTTP-Referer": "https://yourappname.onrender.com",  # change as needed
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "mistral/mistral-7b-instruct",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     return response.json()['choices'][0]['message']['content']

# ------------------

# File: backend/main.py
# FastAPI app to serve endpoints

# import os
# from fastapi import FastAPI, UploadFile, Form
# from fastapi.middleware.cors import CORSMiddleware
# from backend.document_loader import extract_text
# from backend.rag_engine import chunk_text, embed_and_store, search, query_mistral
# import shutil
# from pathlib import Path

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# UPLOAD_DIR = "data/uploaded_files"
# Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


# @app.post("/upload")
# async def upload_file(file: UploadFile):
#     ext = Path(file.filename).suffix
#     temp_path = Path(UPLOAD_DIR) / file.filename
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     text = extract_text(str(temp_path), ext)
#     chunks = chunk_text(text)
#     embed_and_store(chunks)

#     return {"message": "File processed and embedded."}


# @app.post("/ask")
# async def ask_question(question: str = Form(...)):
#     context_chunks = search(question)
#     context = "\n".join(context_chunks)
#     answer = query_mistral(context, question)
#     return {"answer": answer}
