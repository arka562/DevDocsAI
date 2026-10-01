import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { FileText, MessageSquare, Clock } from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ documentsCount: 0, questionsCount: 0, recentConversations: [] });
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/stats`, {
          headers: { Authorization: `Bearer ${user.token}` }
        });
        setStats(res.data);
      } catch (error) {
        console.error('Failed to fetch stats', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [user]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
        <h1 className="text-2xl font-bold mb-8">DevDocs AI</h1>
        <nav className="space-y-4 flex-1">
          <Link to="/dashboard" className="block py-2 px-4 bg-gray-800 rounded">Dashboard</Link>
          <Link to="/documents" className="block py-2 px-4 hover:bg-gray-800 rounded">Documents</Link>
          <Link to="/chat" className="block py-2 px-4 hover:bg-gray-800 rounded">AI Chat</Link>
          <Link to="#" className="block py-2 px-4 hover:bg-gray-800 rounded">History</Link>
          <Link to="#" className="block py-2 px-4 hover:bg-gray-800 rounded">Settings</Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-semibold">Welcome back 👋</h2>
          <div className="flex items-center gap-4">
            <span className="font-medium text-gray-700">👤 {user?.name}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-gray-500 animate-pulse">Loading stats...</div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="flex items-center gap-4 mb-2">
                  <FileText className="text-blue-500" />
                  <h3 className="text-lg font-semibold text-gray-700">Documents Uploaded</h3>
                </div>
                <p className="text-4xl font-bold text-gray-900">{stats.documentsCount}</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="flex items-center gap-4 mb-2">
                  <MessageSquare className="text-green-500" />
                  <h3 className="text-lg font-semibold text-gray-700">Questions Asked</h3>
                </div>
                <p className="text-4xl font-bold text-gray-900">{stats.questionsCount}</p>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Clock size={20} className="text-gray-500" /> Recent Conversations
              </h3>
              {stats.recentConversations.length === 0 ? (
                <p className="text-gray-500">No conversations yet. Go to AI Chat to start!</p>
              ) : (
                <ul className="space-y-3">
                  {stats.recentConversations.map(conv => (
                    <li key={conv._id} className="border-b pb-3 last:border-0 hover:bg-gray-50 rounded px-2 -mx-2 transition-colors">
                      <Link to="/chat" className="block py-1">
                        <p className="font-medium text-gray-800">{conv.title}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(conv.updatedAt).toLocaleDateString()} at {new Date(conv.updatedAt).toLocaleTimeString()}
                        </p>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
