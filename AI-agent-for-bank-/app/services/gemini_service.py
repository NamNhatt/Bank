from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from app.core.config import settings
from app.services.vector_db_service import vector_db_service

class GeminiService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.CHAT_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        self.retriever = vector_db_service.get_retriever()

    async def stream_response(self, question: str, history: list):
        """
        Tạo và thực thi chuỗi RAG để stream câu trả lời.
        """
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
        
        # Nạp lịch sử chat vào memory
        for message in history:
            # ✅ THAY ĐỔI: Sử dụng dấu chấm (.) để truy cập thuộc tính của đối tượng
            if message.role == 'user':
                memory.chat_memory.add_user_message(message.content)
            elif message.role == 'ai':
                memory.chat_memory.add_ai_message(message.content)

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=memory,
        )
        
        # Sử dụng astream để nhận các chunk một cách bất đồng bộ
        async for chunk in chain.astream({"question": question}):
            # Chuỗi này trả về một dictionary, ta cần lấy ra phần 'answer'
            if "answer" in chunk:
                yield chunk["answer"]

# Tạo một instance duy nhất
gemini_service = GeminiService()

