import { useState, useEffect, useRef } from "react";
import "./index.css";

interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
}

interface KnowledgeStats {
  total_documents: number;
  total_chunks: number;
  vector_index_size_mb: number;
  last_sync: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<"chat" | "knowledge" | "settings">("chat");
  const [healthStatus, setHealthStatus] = useState<string>("checking...");
  const [version, setVersion] = useState<string>("");
  const [knowledgeStats, setKnowledgeStats] = useState<KnowledgeStats | null>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "agent",
      content: "Hello. I am the Software Intelligence Platform (SIP) Core Runtime. I am connected to the backend RAG pipeline. How can I assist you with your knowledge bases today?",
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  async function checkHealth() {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/health");
      if (res.ok) {
        const data = await res.json();
        setHealthStatus(data.status);
        setVersion(data.version);
      } else {
        setHealthStatus("unavailable");
      }
    } catch (err) {
      setHealthStatus("unavailable");
    }
  }

  async function fetchKnowledgeStats() {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/knowledge/stats");
      if (res.ok) {
        const data = await res.json();
        setKnowledgeStats(data);
      }
    } catch (err) {
      console.error("Failed to fetch knowledge stats:", err);
    }
  }

  useEffect(() => {
    checkHealth();
    fetchKnowledgeStats();
    const interval = setInterval(checkHealth, 5000); // Check every 5s for fast UI updates
    return () => clearInterval(interval);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content }),
      });

      if (res.ok) {
        const data = await res.json();
        const agentMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "agent",
          content: data.reply + `\n\n[PIPELINE TRACE] Latency: ${data.latency_ms}ms\nSources: ${data.sources.join(', ')}\nDiagnostics: ${JSON.stringify(data.pipeline_diagnostics)}`,
        };
        setMessages((prev) => [...prev, agentMsg]);
      } else {
        const agentMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "agent",
          content: `Error: The backend responded with status ${res.status}. Is the backend running on port 8000?`,
        };
        setMessages((prev) => [...prev, agentMsg]);
      }
    } catch (err) {
      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "agent",
        content: "Network error: Failed to connect to the backend on http://127.0.0.1:8000. Ensure 'uv run uvicorn sip.api.server:app' is running.",
      };
      setMessages((prev) => [...prev, agentMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"></div>
          SIP Workspace
        </div>
        
        <nav className="nav-menu">
          <div 
            className={`nav-item ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            Chat & Retrieval
          </div>
          <div 
            className={`nav-item ${activeTab === "knowledge" ? "active" : ""}`}
            onClick={() => { setActiveTab("knowledge"); fetchKnowledgeStats(); }}
          >
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            Knowledge Base
          </div>
          <div 
            className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
            onClick={() => setActiveTab("settings")}
          >
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Settings
          </div>
        </nav>
      </aside>

      {/* Main App Area */}
      <main className="main-content">
        
        {/* Top Header */}
        <header className="topbar">
          <div style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            {activeTab === "chat" && "Querying Knowledge Workspace"}
            {activeTab === "knowledge" && "Knowledge Base Management"}
            {activeTab === "settings" && "System Configuration"}
          </div>
          <div className="status-badge" title="Backend Connectivity">
            <div className={`status-dot ${healthStatus === "healthy" ? "healthy" : "error"}`}></div>
            <span>{healthStatus === "healthy" ? `SIP Core v${version}` : "Backend Disconnected"}</span>
          </div>
        </header>

        {activeTab === "chat" && (
          <div className="chat-container">
            <div className="chat-history">
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className="message-header">
                    {msg.role === "agent" ? (
                      <><div className="brand-icon" style={{width: 16, height: 16, borderRadius: 4}}></div> SIP Agent</>
                    ) : (
                      <><svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg> You</>
                    )}
                  </div>
                  <div className="message-content" style={{ whiteSpace: "pre-wrap" }}>
                    {msg.content}
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="message agent" style={{ padding: "0.75rem 1.25rem", opacity: 0.7 }}>
                  <div className="message-content">Thinking...</div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
              <div className="input-box">
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask about your codebase or engineering knowledge..."
                  rows={1}
                />
                <button 
                  className="send-btn" 
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                >
                  <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "knowledge" && (
          <div style={{ padding: "2rem" }}>
            <h2 style={{ marginBottom: "1.5rem" }}>Knowledge Base Analytics</h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
              <div style={{ background: "var(--bg-secondary)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--glass-border)" }}>
                <div style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>Total Documents</div>
                <div style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--text-primary)" }}>
                  {knowledgeStats ? knowledgeStats.total_documents : "..."}
                </div>
              </div>
              <div style={{ background: "var(--bg-secondary)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--glass-border)" }}>
                <div style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>Indexed Chunks</div>
                <div style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--text-primary)" }}>
                  {knowledgeStats ? knowledgeStats.total_chunks : "..."}
                </div>
              </div>
              <div style={{ background: "var(--bg-secondary)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--glass-border)" }}>
                <div style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>Vector Database Size (MB)</div>
                <div style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--text-primary)" }}>
                  {knowledgeStats ? knowledgeStats.vector_index_size_mb : "..."}
                </div>
              </div>
              <div style={{ background: "var(--bg-secondary)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--glass-border)" }}>
                <div style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>Last Sync</div>
                <div style={{ fontSize: "1.25rem", fontWeight: 500, color: "var(--text-primary)", marginTop: "1rem" }}>
                  {knowledgeStats ? new Date(knowledgeStats.last_sync).toLocaleString() : "..."}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "settings" && (
          <div style={{ padding: "2rem" }}>
            <h2 style={{ marginBottom: "1.5rem" }}>System Settings</h2>
            <p style={{ color: "var(--text-secondary)" }}>Configure your LLM providers, database URLs, and API keys.</p>
            <div style={{ marginTop: "2rem", background: "var(--bg-secondary)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--glass-border)" }}>
               <h3 style={{ marginBottom: "1rem" }}>Network Architecture</h3>
               <p style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>API Endpoint: http://127.0.0.1:8000</p>
               <p style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>PostgreSQL Vector: sip-db:5432</p>
               <p style={{ color: "var(--text-secondary)", marginBottom: "0.5rem" }}>Qdrant Vector DB: sip-qdrant:6333</p>
               <br/>
               <p style={{ color: "var(--success)", fontWeight: 500 }}>System is configured for local execution.</p>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
