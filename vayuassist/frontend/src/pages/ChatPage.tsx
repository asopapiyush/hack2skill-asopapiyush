import { useState, useEffect, useRef } from 'react';
import '../styles/ChatPage.css';

interface Props {
  token: string;
  userId: string | null;
  userProfile: any;
  onLogout: () => void;
  onProfileUpdate: (profile: any) => void;
}

export default function ChatPage({ token, userProfile, onLogout, onProfileUpdate }: Props) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  
  // Profile edit state
  const [editProfile, setEditProfile] = useState({
    family_size: '',
    location: '',
    region: 'Maharashtra',
    health_conditions: ''
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (userProfile) {
      setEditProfile({
        family_size: userProfile.family_size || '',
        location: userProfile.location || '',
        region: userProfile.region || 'Maharashtra',
        health_conditions: userProfile.health_conditions || ''
      });
      loadChatHistory();
    }
  }, [userProfile, token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8001/chat/history?token=${token}`);
      if (response.ok) {
        const history = await response.json();
        const formattedHistory = [];
        for (const msg of history.reverse()) {
          formattedHistory.push({ type: 'user', content: msg.user_message });
          formattedHistory.push({ type: 'assistant', content: msg.assistant_response, intent: msg.intent });
        }
        setMessages(formattedHistory);
      }
    } catch (err) {
      console.error("Failed to load history", err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          token: token
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessages(prev => [...prev, { 
          type: 'assistant', 
          content: data.response,
          intent: data.intent,
          escalation: data.escalation
        }]);
      } else {
        setMessages(prev => [...prev, { 
          type: 'assistant', 
          content: "Error: " + (data.detail || "Failed to get response"),
          isError: true
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        content: "Network error. Please try again.",
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://localhost:8001/auth/profile?token=${token}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editProfile),
      });

      if (response.ok) {
        onProfileUpdate({ ...userProfile, ...editProfile });
        setShowProfile(false);
      }
    } catch (err) {
      console.error("Failed to update profile", err);
    }
  };

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div className="header-title">
          <h1>VayuAssist</h1>
          {userProfile && <span className="welcome-text">Hi, {userProfile.full_name || userProfile.email}</span>}
        </div>
        <div className="header-actions">
          <button onClick={() => setShowProfile(!showProfile)} className="icon-btn">
            👤 Profile
          </button>
          <button onClick={onLogout} className="icon-btn logout">
            🚪 Logout
          </button>
        </div>
      </header>

      <div className="chat-main">
        {showProfile && (
          <div className="profile-panel">
            <h2>Your Context (helps AI personalize advice)</h2>
            <form onSubmit={handleSaveProfile} className="profile-form">
              <div className="form-group">
                <label>Family Size</label>
                <input 
                  type="number" 
                  value={editProfile.family_size}
                  onChange={(e) => setEditProfile({...editProfile, family_size: e.target.value})}
                  placeholder="e.g., 4"
                />
              </div>
              <div className="form-group">
                <label>Location / Housing Type</label>
                <input 
                  type="text" 
                  value={editProfile.location}
                  onChange={(e) => setEditProfile({...editProfile, location: e.target.value})}
                  placeholder="e.g., Ground floor apartment near river"
                />
              </div>
              <div className="form-group">
                <label>State/Region</label>
                <select 
                  value={editProfile.region}
                  onChange={(e) => setEditProfile({...editProfile, region: e.target.value})}
                >
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Kerala">Kerala</option>
                  <option value="Assam">Assam</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Health Conditions (Optional)</label>
                <input 
                  type="text" 
                  value={editProfile.health_conditions}
                  onChange={(e) => setEditProfile({...editProfile, health_conditions: e.target.value})}
                  placeholder="e.g., Diabetes, Asthma"
                />
              </div>
              <div className="profile-actions">
                <button type="submit" className="primary-btn">Save Profile</button>
                <button type="button" onClick={() => setShowProfile(false)} className="secondary-btn">Cancel</button>
              </div>
            </form>
          </div>
        )}

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h3>Welcome to VayuAssist 🌧️</h3>
              <p>Ask me about monsoon preparedness, travel safety, or emergency help.</p>
              <div className="suggestions">
                <button onClick={() => setInput("What should I stock in my emergency kit?")}>What to stock?</button>
                <button onClick={() => setInput("Is it safe to drive in heavy rain today?")}>Travel advice</button>
                <button onClick={() => setInput("Water is entering my house, what do I do?")} className="emergency-suggest">Flood help</button>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message-row ${msg.type}`}>
                <div className={`message-bubble ${msg.type} ${msg.escalation ? 'escalation' : ''} ${msg.isError ? 'error' : ''}`}>
                  {msg.intent === 'emergency' && msg.type === 'assistant' && 
                    <div className="emergency-banner">⚠️ EMERGENCY INSTRUCTIONS</div>
                  }
                  <div className="message-content" style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message-row assistant">
              <div className="message-bubble assistant loading">
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about monsoon safety..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()} className="send-btn">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
