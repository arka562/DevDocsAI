import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Send, Plus } from 'lucide-react';
import api from '../services/api';
import ChatMessage from '../components/ChatMessage.jsx';

const Chat = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    api.get('/chat/conversations').then((res) => setConversations(res.data));
  }, []);

  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }
    api.get(`/chat/conversations/${conversationId}`).then((res) => setMessages(res.data.messages));
  }, [conversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startNewConversation = async () => {
    const { data } = await api.post('/chat/conversations', {});
    setConversations((prev) => [data, ...prev]);
    navigate(`/chat/${data._id}`);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    let activeId = conversationId;
    if (!activeId) {
      const { data } = await api.post('/chat/conversations', {});
      setConversations((prev) => [data, ...prev]);
      activeId = data._id;
      navigate(`/chat/${activeId}`, { replace: true });
    }

    const question = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question, _id: `temp-${Date.now()}` }]);
    setSending(true);

    try {
      const { data } = await api.post(`/chat/conversations/${activeId}/messages`, { content: question });
      setMessages((prev) => [...prev.filter((m) => !m._id.startsWith('temp-')), data.userMessage, data.assistantMessage]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-3rem)] -m-6">
      <div className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col">
        <button
          onClick={startNewConversation}
          className="m-3 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition"
        >
          <Plus size={16} /> New chat
        </button>
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          {conversations.map((c) => (
            <button
              key={c._id}
              onClick={() => navigate(`/chat/${c._id}`)}
              className={`w-full text-left truncate px-3 py-2 rounded-lg text-sm ${
                c._id === conversationId ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800'
              }`}
            >
              {c.title}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <p className="text-sm text-slate-500">
              Ask a question about your uploaded documentation to get a grounded, cited answer.
            </p>
          )}
          {messages.map((m) => (
            <ChatMessage key={m._id} message={m} />
          ))}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSend} className="p-4 border-t border-slate-800 flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={sending}
            className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 text-sm focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
