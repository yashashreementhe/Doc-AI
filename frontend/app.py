# File: frontend/app.py
# Streamlit UI for uploading files and asking questions

import streamlit as st
import requests

st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("🧠 Document Q&A with RAG + Mistral")

BACKEND_URL = "http://localhost:8000"

uploaded_file = st.file_uploader("Upload your document (PDF, TXT, Excel)", type=["pdf", "txt", "xls", "xlsx"])

if uploaded_file is not None:
    with st.spinner("Uploading and processing file..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        if response.status_code == 200:
            st.success("File uploaded and processed successfully!")
        else:
            st.error("File upload failed.")

if st.text_input("Ask a question about the document:", key="user_question"):
    question = st.session_state["user_question"]
    with st.spinner("Searching and querying Mistral..."):
        response = requests.post(f"{BACKEND_URL}/ask", data={"question": question})
        if response.status_code == 200:
            answer = response.json().get("answer")
            st.markdown(f"**Answer:** {answer}")
        else:
            st.error("Failed to get answer.")


# uvicorn main:app --reload --port 8000
