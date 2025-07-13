import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from document_loader import extract_text
from rag_engine import chunk_text, embed_and_store, search, query_mistral, is_doc_embedded
import shutil
from pathlib import Path


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploaded_files"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile):
    ext = Path(file.filename).suffix
    temp_path = Path(UPLOAD_DIR) / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(str(temp_path), ext)
    chunks = chunk_text(text)
    embed_and_store(chunks)

    return {"message": "File processed and embedded."}

# @app.post("/upload")
# async def upload_file(file: UploadFile):
#     print(f"Received file: {file.filename}")
#     ext = Path(file.filename).suffix
#     temp_path = Path(UPLOAD_DIR) / file.filename
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     print(f"File saved to {temp_path}")

#     text = extract_text(str(temp_path), ext)
#     print(f"Extracted text length: {len(text)}")

#     chunks = chunk_text(text)
#     print(f"Number of chunks: {len(chunks)}")

#     embed_and_store(chunks)
#     print("Embedding and storing complete.")

#     return {"message": "File processed and embedded."}


# @app.post("/ask")
# async def ask_question(question: str = Form(...)):
#     context_chunks = search(question)
#     context = "\n".join(context_chunks)
#     answer = query_mistral(context, question)
#     return {"answer": answer}

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    if not is_doc_embedded():
        return {"answer": "No document has been uploaded yet. Please upload a document first."}

    context_chunks = search(question)
    context = "\n".join(context_chunks)
    answer = query_mistral(context, question)
    return {"answer": answer}

