# app/use_cases/chat_use_case.py
from typing import List, Dict, Any
from ..services.gemini_service import GeminiService
from ..services.embedding_service import EmbeddingService
from ..services.vector_db_service import VectorDBService
from ..core.config import Settings

class ChatUseCase:
    def __init__(self, settings: Settings):
        self.settings = settings
        
        # Khởi tạo các service. Nên sử dụng dependency injection cho các service này
        # trong một ứng dụng lớn hơn, nhưng ở đây ta khởi tạo trực tiếp cho đơn giản.
        self.embedding_service = EmbeddingService() # Dùng settings để cấu hình service
        self.vector_db_service = VectorDBService() # Dùng settings để cấu hình service
        self.gemini_service = GeminiService()
        
        # Lấy dimension từ embedding service nếu có thể, hoặc dùng cài đặt.
        # Điều này cần đảm bảo consistency.
        # Nếu embedding_service là local, nó có thể return dimension
        # Nếu là API, dimension cố định theo mô hình API.
        self.vector_dimension = self.embedding_service.embedding_dimension if hasattr(self.embedding_service, 'embedding_dimension') else self.settings.vector_dimension
        
        # Đảm bảo Vector DB dimension khớp
        if self.vector_db_service.dimension != self.vector_dimension:
             print(f"Warning: Vector DB dimension ({self.vector_db_service.dimension}) does not match Embedding Service dimension ({self.vector_dimension}). This may cause issues.")
             # Có thể cập nhật self.vector_db_service.dimension hoặc set lại
             # self.vector_db_service.dimension = self.vector_dimension # Ví dụ
             # Quan trọng là phải khớp khi tạo index hoặc collection

    async def build_prompt(self, user_query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Xây dựng prompt gửi đến Gemini API."""
        system_message = (
            "Bạn là một trợ lý AI chuyên nghiệp cho ngân hàng [Tên Ngân Hàng Của Bạn]. "
            "Hãy trả lời câu hỏi của khách hàng dựa trên thông tin ngữ cảnh được cung cấp. "
            "Nếu thông tin trong ngữ cảnh không đủ để trả lời câu hỏi, hãy nói rằng bạn không có đủ thông tin "
            "và khuyên khách hàng liên hệ với bộ phận hỗ trợ khách hàng của ngân hàng.\n"
            "Tuyệt đối không tự bịa ra thông tin. Trả lời bằng tiếng Việt.\n\n"
        )
        
        context_text = ""
        if context_chunks:
            context_text = "Ngữ cảnh:\n"
            for i, chunk in enumerate(context_chunks):
                context_text += f"- Nguồn: {chunk.get('source', 'Unknown')}\n"
                context_text += f"  Nội dung: {chunk.get('text', '')}\n"
            context_text += "\n"
        
        prompt = system_message + context_text + f"Câu hỏi của khách hàng: {user_query}\nTrả lời:"
        return prompt

    async def process_message(self, user_query: str) -> str:
        """
        Quy trình RAG chính: Lấy embedding -> Truy vấn Vector DB -> Tạo prompt -> Gọi Gemini -> Trả về.
        """
        if not user_query:
            return "Xin vui lòng nhập câu hỏi của bạn."

        try:
            # 1. Tạo Embedding cho câu hỏi của người dùng
            query_embedding = await self.embedding_service.get_embedding(user_query)
            
            # 2. Truy vấn Vector Database để lấy các đoạn văn bản liên quan
            # top_k có thể được cấu hình, ví dụ 3 hoặc 5 chunk
            context_chunks = await self.vector_db_service.search_similar(query_embedding, top_k=3)
            
            # 3. Xây dựng prompt cuối cùng
            prompt = await self.build_prompt(user_query, context_chunks)
            
            # 4. Gọi Gemini API để tạo câu trả lời
            reply = self.gemini_service.generate_content(prompt)
            
            return reply

        except Exception as e:
            print(f"An error occurred during message processing: {e}")
            # Cần có cơ chế log lỗi chi tiết hơn
            return "Xin lỗi, đã xảy ra lỗi kỹ thuật khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."

    async def close_services(self):
        """Đóng các client service khi ứng dụng tắt."""
        await self.embedding_service.close()
        await self.vector_db_service.close()
        await self.gemini_service.close()