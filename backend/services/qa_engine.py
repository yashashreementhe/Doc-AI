import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"

def ask_question(query: str, context_chunks: list) -> str:
    context = "\n\n".join(context_chunks)
    prompt = f"""Use the following context to answer the question.
    
    Context:
    {context}

    Question: {query}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You're a helpful assistant answering questions based on context."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[❌] Mistral API Error: {e}")
        return "Sorry, I couldn't fetch an answer at this time."
