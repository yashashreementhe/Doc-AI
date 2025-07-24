from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    document_id: str

class AskRequest(BaseModel):
    document_id: str
    query: str

class AskResponse(BaseModel):
    answer: str
