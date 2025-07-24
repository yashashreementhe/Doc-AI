from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import uuid

from backend.services.blob_service import upload_file_to_blob, generate_blob_sas_url
from backend.services.doc_intel import analyze_document_from_blob
from backend.services.embedder import store_document_embeddings, retrieve_relevant_chunks
from backend.services.qa_engine import ask_question

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    blob_name = upload_file_to_blob(temp_filename)
    blob_sas_url = generate_blob_sas_url(blob_name)

    parsed_text = analyze_document_from_blob(blob_sas_url)
    os.remove(temp_filename)

    if parsed_text is None:
        return JSONResponse(status_code=500, content={"error": "Document analysis failed"})

    store_document_embeddings(blob_name, parsed_text)

    return {"message": "Document uploaded and processed", "document_id": blob_name}

@router.post("/ask")
async def ask(document_id: str = Form(...), query: str = Form(...)):
    chunks = retrieve_relevant_chunks(document_id, query)
    answer = ask_question(query, chunks)
    return {"answer": answer}
