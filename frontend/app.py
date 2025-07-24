import streamlit as st
import requests
import os

# === Config ===
BACKEND_URL = "http://localhost:8000"  # Update if deploying

# === Page Setup ===
st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("📄 RAG-powered Chatbot")
st.markdown("Upload documents and ask questions based on their content.")

# === Session Storage ===
if "document_ids" not in st.session_state:
    st.session_state["document_ids"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = {}

# === Upload Section ===
st.subheader("📤 Upload a Document")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])

if uploaded_file:
    with st.spinner("Uploading and analyzing..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        
        if response.status_code == 200:
            document_id = response.json()["document_id"]
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            if document_id not in st.session_state["document_ids"]:
                st.session_state["document_ids"].append(document_id)
        else:
            st.error("❌ Upload failed.")

# === Chat Section ===
st.subheader("💬 Ask a Question")

if len(st.session_state["document_ids"]) == 0:
    st.info("Upload a document to begin.")
else:
    selected_doc = st.selectbox("Select a document", st.session_state["document_ids"])

    query = st.text_input("Ask something about this document...")

    if query:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/ask",
                data={"document_id": selected_doc, "query": query}
            )
            if response.status_code == 200:
                answer = response.json()["answer"]

                if selected_doc not in st.session_state["chat_history"]:
                    st.session_state["chat_history"][selected_doc] = []
                
                st.session_state["chat_history"][selected_doc].append((query, answer))

                st.success(answer)
            else:
                st.error("❌ Failed to get answer.")

# === Chat History ===
if st.session_state["chat_history"]:
    st.subheader("📜 Chat History")
    for doc_id, history in st.session_state["chat_history"].items():
        st.markdown(f"**Document ID:** `{doc_id}`")
        for i, (q, a) in enumerate(history):
            st.markdown(f"- **Q{i+1}:** {q}")
            st.markdown(f"  **A{i+1}:** {a}")
