from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Khai báo tất cả các biến bắt buộc phải có trong file .env
    GOOGLE_API_KEY: str
    GEMINI_EMBEDDING_MODEL: str
    CHAT_MODEL_NAME: str
    
    # Biến này sẽ đọc từ .env nếu có, nếu không sẽ dùng giá trị mặc định
    # Đổi tên thành VECTOR_DB_PATH để khớp với file .env
    VECTOR_DB_PATH: str = "./vectorstore/db_faiss" 
    
    # Cấu hình để đọc file .env
    model_config = SettingsConfigDict(env_file=".env")

# Tạo một instance duy nhất để sử dụng trong toàn bộ ứng dụng
settings = Settings()