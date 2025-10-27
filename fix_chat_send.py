from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

@app.post("/chat/send")
async def chat_send(chat_message: ChatMessage):
    # Your existing chat logic here
    return {"guide": "White Buffalo", "message": "Wisdom", "user_message": chat_message.message}
