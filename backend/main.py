from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import rag

# import routes.rag

app = FastAPI(title="RAG App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag.router)
