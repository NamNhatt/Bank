import pickle
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import settings

class VectorDBService:
    def __init__(self):
        # Tự tạo model embedding ngay tại đây
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Tải cơ sở dữ liệu vector từ đường dẫn trong file config
        self.db = FAISS.load_local(
            settings.VECTOR_DB_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print(f"✅ Vector DB đã được tải thành công (sử dụng model: {settings.GEMINI_EMBEDDING_MODEL}).")

    # ✅ THAY ĐỔI: Thêm lại phương thức get_retriever
    def get_retriever(self, k=5):
        """Tạo và trả về một retriever từ cơ sở dữ liệu vector."""
        return self.db.as_retriever(search_kwargs={'k': k})

# Tạo một instance duy nhất để tái sử dụng trong toàn bộ ứng dụng
vector_db_service = VectorDBService()

