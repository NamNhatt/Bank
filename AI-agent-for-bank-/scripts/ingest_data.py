import os
import sys
import time # Thêm thư viện time để tạo độ trễ

# Thêm thư mục gốc vào path để import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Import các thư viện cần thiết
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.core.config import settings

def main():
    print("--- Bắt đầu nạp dữ liệu ---")
    
    # Khởi tạo model embedding
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY
    )

    # Tải và xử lý tài liệu
    loader = DirectoryLoader('./data', glob="**/*.txt", show_progress=True)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    print(f"Đã chia thành {len(docs)} đoạn văn bản.")
    
    db_path = settings.VECTOR_DB_PATH 
    print(f"Đang tạo vector và lưu vào FAISS tại: '{db_path}'...")
    
    # ✅ THAY ĐỔI: Xử lý theo từng lô nhỏ để tránh lỗi server
    
    # 1. Tạo một cơ sở dữ liệu rỗng trước
    # Lấy vector của đoạn văn bản đầu tiên để khởi tạo DB
    first_doc_text = [docs[0].page_content]
    first_embedding = embeddings.embed_documents(first_doc_text)
    
    # Tạo index với kích thước vector chính xác
    index = FAISS.from_embeddings(text_embeddings=list(zip(first_doc_text, first_embedding)), embedding=embeddings)
    
    # Thêm các tài liệu còn lại theo từng lô
    batch_size = 20  # Mỗi lần chỉ xử lý 20 đoạn
    for i in range(1, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        print(f"   - Đang xử lý lô {i//batch_size + 1} (gồm {len(batch)} đoạn)...")
        index.add_documents(batch)
        print("   - Nghỉ 1 giây để tránh quá tải API...")
        time.sleep(1) # Nghỉ 1 giây giữa các lần gọi

    # 2. Lưu cơ sở dữ liệu sau khi đã thêm tất cả
    index.save_local(db_path)
    
    print(f"--- Hoàn tất! Đã lưu DB thành công ---")

if __name__ == "__main__":
    main()

