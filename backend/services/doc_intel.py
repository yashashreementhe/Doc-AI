import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
API_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
API_VERSION = "2023-07-31"
MODEL = "prebuilt-document"

def analyze_document_from_blob(blob_sas_url: str):
    url = f"{ENDPOINT}/formrecognizer/documentModels/{MODEL}:analyze?api-version={API_VERSION}"

    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY,
        "Content-Type": "application/json"
    }

    body = {"urlSource": blob_sas_url}

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        operation_url = response.headers["operation-location"]

        # Polling until done
        while True:
            result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": API_KEY})
            result_json = result.json()
            if result_json.get("status") in ["succeeded", "failed"]:
                break
            time.sleep(2)

        if result_json["status"] == "succeeded":
            text = ""
            for page in result_json["analyzeResult"]["content"].splitlines():
                text += page + "\n"
            return text.strip()
        else:
            return None
    except Exception as e:
        print(f"[❌] Document Intelligence Error: {e}")
        return None
