# scripts/chunk_data.py
import os
import json
from typing import List, Dict, Any
import sys # Import sys

# --- Bắt đầu phần thêm vào để fix ModuleNotFoundError ---
# Lấy đường dẫn tuyệt đối của thư mục hiện tại mà script đang chạy
current_dir = os.path.dirname(os.path.abspath(__file__))
# Lấy đường dẫn thư mục gốc của dự án (thư mục chứa thư mục 'scripts')
project_root = os.path.dirname(current_dir)

# Thêm thư mục gốc vào sys.path nếu nó chưa có
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- Kết thúc phần thêm vào ---

# Thư viện của LangChain để chia nhỏ văn bản
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import cấu hình để lấy các tham số CHUNK_SIZE và CHUNK_OVERLAP
from app.core.config import settings 

# Thư mục chứa dữ liệu gốc
DATA_DIR = "data"
# Tệp đầu ra chứa các đoạn văn bản đã chia nhỏ
OUTPUT_FILE = "processed_data.json" 

def load_documents(directory: str) -> Dict[str, str]:
    """
    Tải tất cả các tệp văn bản (.txt) từ một thư mục.
    Trả về một dictionary: {tên_file: nội_dung_file}.
    """
    documents = {}
    if not os.path.exists(directory):
        print(f"Thư mục dữ liệu '{directory}' không tồn tại. Vui lòng tạo thư mục và thêm các tệp văn bản vào đó.")
        return documents

    print(f"Đang tải tài liệu từ thư mục: {directory}")
    for filename in os.listdir(directory):
        if filename.endswith(".txt"): # Chỉ xử lý tệp .txt
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    documents[filename] = f.read()
                print(f"  - Đã tải: {filename}")
            except Exception as e:
                print(f"  - Lỗi khi tải {filename}: {e}")
    return documents

def chunk_documents(documents: Dict[str, str], chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
    """
    Chia nhỏ các tài liệu thành các đoạn nhỏ hơn.
    documents: Dictionary {tên_file: nội_dung_file}.
    chunk_size: Kích thước tối đa của mỗi đoạn văn bản.
    chunk_overlap: Số ký tự chồng lấn giữa các đoạn liên tiếp.
    Trả về: Một danh sách các dictionary, mỗi dictionary là một đoạn văn bản
             với các khóa 'text', 'source', 'id'.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len, # Sử dụng số ký tự để tính độ dài
        is_separator_regex=False,
    )
    
    all_chunks = []
    print(f"\nĐang chia nhỏ văn bản với chunk_size={chunk_size}, chunk_overlap={chunk_overlap}...")

    for source, text in documents.items():
        if not text.strip(): # Bỏ qua các tệp rỗng
            print(f"  - Bỏ qua tệp rỗng: {source}")
            continue
            
        chunks = text_splitter.split_text(text)
        print(f"  - Tệp '{source}' được chia thành {len(chunks)} đoạn.")
        
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": source, # Lưu tên tệp gốc
                "id": f"{source.split('.')[0]}_chunk_{i}" # Tạo ID duy nhất cho mỗi chunk
            })
            
    print(f"\nTổng cộng đã tạo được {len(all_chunks)} đoạn văn bản.")
    return all_chunks

def save_chunks(chunks: List[Dict[str, Any]], output_filepath: str) -> None:
    """
    Lưu danh sách các đoạn văn bản vào một tệp JSON.
    """
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu thành công {len(chunks)} đoạn văn bản vào tệp: {output_filepath}")
    except Exception as e:
        print(f"Lỗi khi lưu các đoạn văn bản vào tệp '{output_filepath}': {e}")

if __name__ == "__main__":
    # Lấy các tham số chunking từ cấu hình
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap
    
    # 1. Tải tài liệu
    loaded_documents = load_documents(DATA_DIR)
    
    if not loaded_documents:
        print("Không có tài liệu nào được tải. Vui lòng kiểm tra thư mục 'data/'.")
    else:
        # 2. Chia nhỏ tài liệu
        processed_chunks = chunk_documents(loaded_documents, chunk_size, chunk_overlap)
        
        # 3. Lưu kết quả
        if processed_chunks:
            save_chunks(processed_chunks, OUTPUT_FILE)
        else:
            print("Không có đoạn văn bản nào được tạo ra.")