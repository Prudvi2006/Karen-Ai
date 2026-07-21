import "../App.css";
import { Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, useEffect, useRef } from "react";

export default function homepage() {

  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello 👋 How can I help you today?" },
  ]);

  const [input, setInput] = useState("");
  const [chatId, setChatId] = useState("");
  const [chats, setChats] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState("groq");

  const sendMessage = async () => {

    if (!input.trim()) return;

    const messageText = input;
    const userMessage = { role: "user", text: messageText };

    setInput("");

    // add user message
    setMessages(prev => [...prev, userMessage]);

    // add empty bot message
    setMessages(prev => [...prev, { role: "bot", text: "" }]);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          chat_id: chatId,
          message: messageText,
          model: selectedModel,
        }),
      });

      if (!res.ok || !res.body) {
        throw new Error("Network error");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let botReply = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        botReply += decoder.decode(value, { stream: true });

        // update ONLY last message (important fix)
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "bot",
            text: botReply,
          };
          return updated;
        });
      }
    } catch (error) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "bot",
          text: "Error connecting to server ❌",
        };
        return updated;
      });
    }
  };




  const uploadFile = async (file) => {
    if (!file) return;

    setUploadStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    // Decide which API to call
    let endpoint = "";

    if (file.type === "application/pdf") {
      endpoint = "http://localhost:8000/upload";
    } else if (file.type.startsWith("image/")) {
      endpoint = "http://localhost:8000/upload-image";
    } else {
      setUploadStatus("❌ Unsupported file type");
      return;
    }

    try {
      const token = localStorage.getItem("token");
      console.log("Token:", token);
console.log("Chat ID:", chatId);

      const res = await fetch(`${endpoint}?chat_id=${chatId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();

      setUploadStatus(`✅ ${data.filename} uploaded`);
    } catch (err) {
      setUploadStatus("❌ Upload failed");
    }
  };



  const createNewChat = async () => {
    const token = localStorage.getItem("token");
    const res = await fetch("http://localhost:8000/new-chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        title: "New Chat",
      }),
    });
    const data = await res.json();
    setChatId(data.chat_id);
    setMessages([
      { role: "bot", text: "Hello 👋 How can I help you today?" }
    ]);
    await loadChats();
  };

  const loadChat = async (id) => {
    const token = localStorage.getItem("token");
    console.log(token);
    const res = await fetch(
      `http://localhost:8000/messages/${id}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    const data = await res.json();

    setMessages(data);
  };

  const loadChats = async () => {
    const token = localStorage.getItem("token");

    const res = await fetch("http://localhost:8000/chats", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await res.json();

    setChats(data);
  };
  useEffect(() => {
    loadChats();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);




  const deleteChat = async (id) => {
    const token = localStorage.getItem("token");
    const res = await fetch(`http://localhost:8000/chat/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      alert("Failed to delete chat");
      return;
    }

    await loadChats();      // Reload sidebar

    if (chatId === id) {
      setChatId("");
      setMessages([]);
    }

  };

  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const initialize = async () => {
      const token = localStorage.getItem("token");

      const res = await fetch("http://localhost:8000/chats", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      setChats(data);

      if (data.length > 0) {
        // Open the latest chat
        setChatId(data[0].chat_id);
        loadChat(data[0].chat_id);
      } else {
        // Create the first chat
        await createNewChat();
      }
    };

    initialize();
  }, []);


  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">Karen AI</div>

        <button onClick={createNewChat}>+ New Chat</button>

        <div className="history">
          {chats.map((chat) => (
            <div key={chat.chat_id} className="history-item">
              <span
                className="chat-title"
                onClick={() => {
                  setChatId(chat.chat_id);
                  loadChat(chat.chat_id);
                }}
              >
                {chat.title}
              </span>

              <button
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation(); // Prevent opening the chat
                  if (window.confirm("Delete this chat?")) {
                    deleteChat(chat.chat_id);
                  }
                }}
              >
                🗑️
              </button>
            </div>
          ))}

        </div>
      </aside>


      {/* Chat Area */}
      <main className="chatArea">
        <div className="chatContainer">

          {/* Messages */}
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div className="bubble">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}

            <div ref={messagesEndRef}></div>
          </div>

          {/* Input */}
          <div className="inputBar">
            {selectedFile && (
              <div className="filePreview">

                {selectedFile.type.startsWith("image/") ? (
                  <div className="previewCard">

                    <img
                      src={URL.createObjectURL(selectedFile)}
                      alt="preview"
                    />

                    <button
                      className="removePreview"
                      onClick={() => {
                        setSelectedFile(null);
                        fileInputRef.current.value = "";
                      }}
                    >
                      ✕
                    </button>

                  </div>
                ) : (
                  <div className="pdfCard">

                    <span>📄 {selectedFile.name}</span>

                    <button
                      className="removePreview"
                      onClick={() => {
                        setSelectedFile(null);
                        fileInputRef.current.value = "";
                      }}
                    >
                      ✕
                    </button>

                  </div>
                )}

              </div>
            )}
            <div className="inputRow">

              <div className="modelSelector">
                <label>Model:</label>

                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                >
                  <option value="gemini">Gemini</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="groq">GROQ</option>
                </select>
              </div>

              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.webp"
                ref={fileInputRef}
                hidden
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (!file) return;

                  setSelectedFile(file);
                  uploadFile(file);
                }}
              />

              <button
                className="uploadBtn"
                onClick={() => fileInputRef.current.click()}
              >
                📎
              </button>

              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Message ChatGPT..."
              />

              <button onClick={sendMessage}>
                ↑
              </button>

            </div>

          </div>


        </div>
      </main>
    </div>
  );
}





