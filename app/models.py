from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    text: str
    chart1: str  # base64-encoded image
    chart2: str  # base64-encoded image 