from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service

# ✅ THAY ĐỔI: Import đúng instance `gemini_service` thay vì các service con
# Điều này giúp endpoint gọn gàng hơn

router = APIRouter()

@router.post("/query")
async def handle_chat_query(request: ChatRequest):
    """
    Endpoint để xử lý yêu cầu chat và trả về câu trả lời dạng stream.
    """
    try:
        # Sử dụng async generator để nhận stream từ service
        async def stream_generator():
            full_response = ""
            # Giả định gemini_service có một phương thức stream
            async for chunk in gemini_service.stream_response(request.question, request.history):
                full_response += chunk
                yield chunk
        
        return StreamingResponse(stream_generator(), media_type="text/plain")

    except Exception as e:
        print(f"Lỗi xảy ra trong quá trình xử lý chat: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý nội bộ.")
