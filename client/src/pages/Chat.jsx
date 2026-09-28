import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Send, PlusCircle, MessageSquare, Loader2 } from 'lucide-react';

const Chat = () => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      fetchMessages(activeConvId);
    }
  }, [activeConvId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/chat/conversations', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setConversations(res.data);
      if (res.data.length > 0 && !activeConvId) {
        setActiveConvId(res.data[0]._id);
      }
    } catch (error) {
      console.error('Failed to fetch conversations', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/chat/conversations', {}, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setConversations([res.data, ...conversations]);
      setActiveConvId(res.data._id);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create conversation', error);
    }
  };

  const fetchMessages = async (id) => {
    try {
      const res = await axios.get(`http://localhost:5000/api/chat/conversations/${id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setMessages(res.data);
    } catch (error) {
      console.error('Failed to fetch messages', error);
    }
  }; 

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeConvId) return;

    const userMsg = { role: 'user', content: input, _id: Date.now().toString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(
        `http://localhost:5000/api/chat/conversations/${activeConvId}/messages`,
        { content: userMsg.content },
        { headers: { Authorization: `Bearer ${user.token}` } }
      );
      setMessages((prev) => [...prev, res.data]);
      
      // Update conversation title if needed
      fetchConversations();
    } catch (error) {
      console.error('Failed to send message', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', _id: Date.now().toString() }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
        <h1 className="text-2xl font-bold mb-8">DevDocs AI</h1>
        <nav className="space-y-2 flex-1">
          <Link to="/dashboard" className="block py-2 px-4 hover:bg-gray-800 rounded">Dashboard</Link>
          <Link to="/documents" className="block py-2 px-4 hover:bg-gray-800 rounded">Documents</Link>
          <Link to="/chat" className="block py-2 px-4 bg-gray-800 rounded">AI Chat</Link>
          <hr className="border-gray-700 my-4" />
          <button 
            onClick={createNewConversation}
            className="flex items-center gap-2 w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded text-sm mb-4"
          >
            <PlusCircle size={16} /> New Chat
          </button>
          
          <div className="overflow-y-auto max-h-[50vh]">
            {conversations.map(conv => (
              <button
                key={conv._id}
                onClick={() => setActiveConvId(conv._id)}
                className={`flex items-center gap-2 w-full text-left py-2 px-3 rounded text-sm truncate ${
                  activeConvId === conv._id ? 'bg-gray-800' : 'hover:bg-gray-800'
                }`}
              >
                <MessageSquare size={14} className="flex-shrink-0" />
                <span className="truncate">{conv.title}</span>
              </button>
            ))}
          </div>
        </nav>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {!activeConvId ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
              <p>Select or create a conversation to start chatting.</p>
            </div>
          </div>
        ) : (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8">
              <div className="max-w-3xl mx-auto space-y-6">
                {messages.length === 0 && !loading && (
                  <div className="text-center text-gray-500 mt-20">
                    <p>Ask a question about your uploaded documentation!</p>
                  </div>
                )}
                
                {messages.map((msg) => (
                  <div key={msg._id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-lg p-4 shadow-sm ${
                      msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
                    }`}>
                      <div className="prose prose-sm max-w-none">
                        {msg.role === 'user' ? (
                          msg.content
                        ) : (
                          <ReactMarkdown
                            components={{
                              code({node, inline, className, children, ...props}) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                  <SyntaxHighlighter
                                    {...props}
                                    children={String(children).replace(/\n$/, '')}
                                    style={vscDarkPlus}
                                    language={match[1]}
                                    PreTag="div"
                                  />
                                ) : (
                                  <code {...props} className={className}>
                                    {children}
                                  </code>
                                )
                              }
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        )}
                      </div>
                      
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <p className="text-xs font-semibold text-gray-500 mb-2">Sources:</p>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {msg.sources.map((source, idx) => (
                              <li key={idx} className="flex items-center gap-1">
                                📄 {source.documentName}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white border rounded-lg p-4 shadow-sm flex items-center gap-2">
                      <Loader2 size={16} className="animate-spin text-gray-500" />
                      <span className="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Form with Developer Tools */}
            <div className="bg-white border-t p-4">
              <div className="max-w-3xl mx-auto mb-2 flex gap-2 overflow-x-auto pb-1">
                <button
                  onClick={() => setInput("Explain this code based on the documentation:\n\n```\n[PASTE CODE HERE]\n```\n")}
                  className="whitespace-nowrap text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full border transition-colors"
                >
                  💡 Explain Code
                </button>
                <button
                  onClick={() => setInput("I am getting this error:\n\n```\n[PASTE ERROR HERE]\n```\n\nPlease explain what happened, why it happened, how to fix it, and provide an example.")}
                  className="whitespace-nowrap text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full border transition-colors"
                >
                  🐞 Explain Error
                </button>
                <button
                  onClick={() => setInput("Generate a code example for:\n[DESCRIBE WHAT YOU WANT HERE]")}
                  className="whitespace-nowrap text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full border transition-colors"
                >
                  🛠️ Generate Example
                </button>
              </div>
              <form onSubmit={sendMessage} className="max-w-3xl mx-auto relative flex items-end gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage(e);
                    }
                  }}
                  placeholder="Ask a question or use a developer tool..."
                  className="w-full bg-gray-50 border rounded-xl pl-4 pr-12 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                  style={{ minHeight: '60px', maxHeight: '200px' }}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || loading}
                  className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <Send size={18} />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Chat;
