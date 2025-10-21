// Lấy các element từ HTML
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const API_URL = 'http://localhost:8000/api/v1/chat/query'; 

let chatHistory = [];

// --- THÊM MỚI: Biến trạng thái và AbortController ---
let isGenerating = false;
let abortController = null;

// --- THÊM MỚI: SVG icon cho nút Dừng ---
const sendIconSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405Z" /></svg>`;
const stopIconSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M4.5 4.5a3 3 0 0 0-3 3v9a3 3 0 0 0 3 3h9a3 3 0 0 0 3-3v-9a3 3 0 0 0-3-3h-9Z" /></svg>`;


// --- THÊM MỚI: Hàm chuyển đổi trạng thái nút ---
function toggleButtonState(generating) {
    isGenerating = generating;
    if (isGenerating) {
        sendBtn.innerHTML = stopIconSVG;
        sendBtn.classList.add('stop');
        sendBtn.setAttribute('aria-label', 'Dừng');
    } else {
        sendBtn.innerHTML = sendIconSVG;
        sendBtn.classList.remove('stop');
        sendBtn.setAttribute('aria-label', 'Gửi');
    }
}

// Hàm thêm tin nhắn vào giao diện
function addMessage(text, sender) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender);
    const pElement = document.createElement('p');
    pElement.innerText = text;
    messageContainer.appendChild(pElement);
    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
    return { messageContainer, pElement };
}

// --- THÊM MỚI: Hàm dừng việc tạo câu trả lời ---
function stopGeneration() {
    if (abortController) {
        abortController.abort();
        console.log("Yêu cầu đã được hủy.");
    }
}

// Hàm chính để gửi tin nhắn (ĐÃ SỬA ĐỔI)
async function sendMessage() {
    const question = userInput.value.trim();
    if (!question) return;

    // --- SỬA ĐỔI: Chuyển nút sang trạng thái "Dừng" ---
    toggleButtonState(true);
    
    addMessage(question, 'user');
    chatHistory.push({ role: 'user', content: question });
    userInput.value = '';

    const { messageContainer, pElement } = addMessage("...", 'ai');
    pElement.innerText = "";
    
    let fullAiResponse = "";
    
    // --- SỬA ĐỔI: Tạo AbortController mới cho mỗi yêu cầu ---
    abortController = new AbortController();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                question: question, 
                history: chatHistory.slice(0, -1)
            }),
            // --- SỬA ĐỔI: Gắn signal vào yêu cầu fetch ---
            signal: abortController.signal
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            let chunk = decoder.decode(value, { stream: true });
            
            if (chunk.startsWith("SOURCES:")) {
                const sourcesJson = chunk.substring(8);
                const sources = JSON.parse(sourcesJson);
                const sourcesDiv = document.createElement('div');
                sourcesDiv.classList.add('message-sources');
                sourcesDiv.innerText = "Nguồn:";
                sources.forEach(sourceName => {
                    const sourceTag = document.createElement('span');
                    sourceTag.classList.add('source-tag');
                    sourceTag.innerText = sourceName;
                    sourcesDiv.appendChild(sourceTag);
                });
                messageContainer.appendChild(sourcesDiv);
            } else {
                fullAiResponse += chunk;
                pElement.innerText = fullAiResponse;
            }
            
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {
        // --- SỬA ĐỔI: Kiểm tra xem lỗi có phải do người dùng hủy không ---
        if (error.name === 'AbortError') {
            pElement.innerText += " [Đã dừng]";
        } else {
            console.error("Lỗi khi gọi API:", error);
            pElement.innerText = "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.";
        }
    } finally {
        if (fullAiResponse) {
             chatHistory.push({ role: 'ai', content: fullAiResponse });
        }
        // --- SỬA ĐỔI: Luôn chuyển nút về trạng thái "Gửi" khi kết thúc ---
        toggleButtonState(false);
    }
}

// --- SỬA ĐỔI: Logic của nút bấm ---
sendBtn.addEventListener('click', () => {
    if (isGenerating) {
        stopGeneration();
    } else {
        sendMessage();
    }
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isGenerating) {
        sendMessage();
    }
});