import customtkinter as ctk
import requests
import threading
from PIL import Image
import os
import speech_recognition as sr # Thêm thư viện nhận dạng giọng nói

# --- Cấu hình ---
API_URL = "http://localhost:8000/api/v1/chat/query"
APP_TITLE = "Trợ lý Ảo Ngân hàng"
WINDOW_SIZE = "800x600"

# --- Màu sắc và Font chữ ---
BG_COLOR = "#242424"
INPUT_BG_COLOR = "#343638"
USER_BUBBLE_COLOR = "#2b59b5"
AI_BUBBLE_COLOR = "#3e4042"
TEXT_COLOR = "white"
FONT_FAMILY = "Roboto"

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.configure(fg_color=BG_COLOR)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Tạo một khung chính để chứa tất cả các thành phần khác ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # --- Tạo các thành phần giao diện và đặt chúng vào main_frame ---
        self.chat_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # ✅ THAY ĐỔI: Xóa dòng code gây lỗi ở đây.
        # CTkScrollableFrame không có thuộc tính grid_column_configure.
        # Bố cục của các bubble bên trong đã được xử lý khi thêm chúng vào.

        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)

        self.send_icon = self.load_icon("send_icon.png")
        self.mic_icon = self.load_icon("mic_icon.png")

        self.user_input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Nhập câu hỏi của bạn...",
            font=(FONT_FAMILY, 16), height=40, corner_radius=15,
            fg_color=INPUT_BG_COLOR, border_width=0
        )
        self.user_input_entry.grid(row=0, column=0, sticky="ew")
        self.user_input_entry.bind("<Return>", self.on_send_pressed)

        self.send_button = ctk.CTkButton(
            input_frame, image=self.send_icon, text="Gửi",
            width=80, height=36, fg_color=USER_BUBBLE_COLOR,
            hover_color="#1e418a", command=self.on_send_pressed
        )
        self.send_button.grid(row=0, column=1, padx=(10, 5))

        self.mic_button = ctk.CTkButton(
            input_frame, image=self.mic_icon, text="🎙️",
            width=40, height=36, font=(FONT_FAMILY, 18),
            fg_color="transparent", hover_color="#4a4d50",
            command=self.on_mic_pressed # Gán lệnh mới
        )
        self.mic_button.grid(row=0, column=2, padx=(0, 0))

        # --- Khởi tạo các biến ---
        self.chat_history = []
        self.ai_bubble_label = None
        self.add_chat_bubble("ai", "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?")

    def load_icon(self, filename, size=(20, 20)):
        if os.path.exists(filename):
            try:
                return ctk.CTkImage(Image.open(filename), size=size)
            except Exception as e:
                print(f"Lỗi khi tải ảnh '{filename}': {e}")
        print(f"Cảnh báo: Không tìm thấy file icon '{filename}'.")
        return None

    def add_chat_bubble(self, role, text):
        if role == "user":
            bubble_color = USER_BUBBLE_COLOR
            justify = "right"; anchor = "e"; padx = (50, 0)
        else:
            bubble_color = AI_BUBBLE_COLOR
            justify = "left"; anchor = "w"; padx = (0, 50)
            
        bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color=bubble_color, corner_radius=15)
        # Khung bubble sẽ tự động co giãn theo chiều rộng nếu cần
        bubble_frame.pack(anchor=anchor, padx=padx, pady=4, fill="x")
        
        message_label = ctk.CTkLabel(
            bubble_frame, text=text, font=(FONT_FAMILY, 16),
            wraplength=500, justify=justify, text_color=TEXT_COLOR
        )
        message_label.pack(padx=15, pady=10)
        return message_label
    
    # --- TÍCH HỢP CHUYỂN ĐỔI GIỌNG NÓI ---
    
    def on_mic_pressed(self):
        """Xử lý giao diện và bắt đầu luồng nhận dạng giọng nói."""
        self.user_input_entry.delete(0, "end")
        self.user_input_entry.insert(0, "Đang lắng nghe, mời bạn nói...")
        self.mic_button.configure(state="disabled", fg_color="#555555")
        self.send_button.configure(state="disabled")

        threading.Thread(target=self.recognize_and_send, daemon=True).start()

    def recognize_and_send(self):
        """Lắng nghe từ micro, chuyển thành văn bản và tự động gửi đi."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("Recognizing...")
                # Sử dụng Google Web Speech API để nhận dạng tiếng Việt
                text = recognizer.recognize_google(audio, language="vi-VN")
                print(f"Bạn đã nói: {text}")

                self.after(0, self.process_recognized_text, text)
            except sr.WaitTimeoutError:
                self.after(0, self.update_input_placeholder, "Không nghe thấy gì, thử lại.")
            except sr.UnknownValueError:
                self.after(0, self.update_input_placeholder, "Không thể nhận dạng giọng nói.")
            except sr.RequestError as e:
                self.after(0, self.update_input_placeholder, f"Lỗi dịch vụ: {e}")
            finally:
                self.after(0, self.reset_input_state)

    def process_recognized_text(self, text):
        """Điền văn bản đã nhận dạng vào ô và tự động gửi."""
        self.user_input_entry.delete(0, "end")
        self.user_input_entry.insert(0, text)
        self.on_send_pressed()

    def update_input_placeholder(self, text):
        """Hiển thị thông báo trạng thái/lỗi trong ô nhập liệu."""
        self.user_input_entry.delete(0, "end")
        self.user_input_entry.insert(0, text)

    def reset_input_state(self):
        """Kích hoạt lại các nút và xóa placeholder text nếu cần."""
        self.mic_button.configure(state="normal", fg_color="transparent")
        self.send_button.configure(state="normal")
        current_text = self.user_input_entry.get()
        if "Đang lắng nghe" in current_text or "Lỗi" in current_text or "Không" in current_text:
            self.user_input_entry.delete(0, "end")
            
    # --- CÁC HÀM XỬ LÝ CHAT CÓ SẴN ---

    def on_send_pressed(self, event=None):
        user_text = self.user_input_entry.get()
        if not user_text.strip(): return
        self.add_chat_bubble("user", user_text)
        self.chat_history.append({"role": "user", "content": user_text})
        self.user_input_entry.delete(0, "end")
        self.send_button.configure(state="disabled")
        self.mic_button.configure(state="disabled")
        threading.Thread(target=self.get_ai_response, args=(user_text,)).start()

    def update_ai_bubble_text(self, chunk):
        if self.ai_bubble_label:
            current_text = self.ai_bubble_label.cget("text")
            self.ai_bubble_label.configure(text=current_text + chunk)

    def get_ai_response(self, question):
        self.ai_bubble_label = self.add_chat_bubble("ai", "")
        full_ai_response = ""
        try:
            response = requests.post(
                API_URL,
                json={"question": question, "history": self.chat_history[:-1]},
                stream=True
            )
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    self.after(0, self.update_ai_bubble_text, chunk)
                    full_ai_response += chunk
        except requests.exceptions.RequestException as e:
            error_message = f"[Lỗi kết nối: {e}]"
            self.after(0, self.update_ai_bubble_text, error_message)
            full_ai_response = error_message
        
        self.chat_history.append({"role": "ai", "content": full_ai_response.strip()})
        self.ai_bubble_label = None
        self.after(0, self.reset_input_state)

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()

