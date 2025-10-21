# app/schemas/chat.py
from pydantic import BaseModel
from typing import List, Dict, Any

# ✅ THAY ĐỔI: Thêm một schema để định nghĩa cấu trúc của một tin nhắn trong lịch sử
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    # ✅ THAY ĐỔI: Thêm trường 'history'
    # Nó là một danh sách các tin nhắn (ChatMessage) và có thể rỗng
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    """
    Schema cho response trả về của API chat.
    """
    answer: str