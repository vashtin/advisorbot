
// Select important elements
const chatWindow = document.querySelector(".chat-window");
const input = document.querySelector(".input-area input");
const sendBtn = document.querySelector(".input-area button");

const API_URL = "http://127.0.0.1:8000/chat";

// Helper: add chat bubbles
function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;
  msg.appendChild(bubble);
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Helper: show "AI Assistant is typing..."
function showTyping() {
  const msg = document.createElement("div");
  msg.classList.add("message", "bot", "typing");
  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = "AI Assistant is typing...";
  msg.appendChild(bubble);
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return msg;
}

// Send message when user clicks button or presses Enter
function sendMessage() {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  const typingBubble = showTyping();

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  })
    .then(res => res.json())
    .then(data => {
      chatWindow.removeChild(typingBubble);

      if (data.major) {
        const response = `${data.major} — ${data.college}.
In-State: ${data.tuition_in_state}, Out-of-State: ${data.tuition_out_state}.
${data.description}`;
        addMessage(response, "bot");
      } else if (data.message) {
        addMessage(data.message, "bot");
      }
    })
    .catch(err => {
      chatWindow.removeChild(typingBubble);
      addMessage("⚠️ Error connecting to the server.", "bot");
      console.error(err);
    });
}

// Send on click or Enter key
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});
