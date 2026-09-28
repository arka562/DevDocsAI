import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, MessageSquare } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';

const Dashboard = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/documents'), api.get('/chat/conversations')])
      .then(([docsRes, convosRes]) => {
        setDocuments(docsRes.data);
        setConversations(convosRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const questionsAsked = conversations.length;

  return (
    <div>
      <h2 className="text-xl font-semibold text-white mb-1">Welcome back, {user?.name}</h2>
      <p className="text-sm text-slate-500 mb-6">Here's a snapshot of your workspace.</p>

      <div className="grid grid-cols-2 gap-4 mb-8 max-w-md">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <FileText size={16} /> Documents
          </div>
          <p className="text-2xl font-bold text-white">{loading ? '-' : documents.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
            <MessageSquare size={16} /> Conversations
          </div>
          <p className="text-2xl font-bold text-white">{loading ? '-' : questionsAsked}</p>
        </div>
      </div>

      <h3 className="text-sm font-semibold text-slate-300 mb-3">Recent documents</h3>
      {documents.length === 0 ? (
        <p className="text-sm text-slate-500">
          No documents yet.{' '}
          <Link to="/documents" className="text-indigo-400 hover:underline">
            Upload one
          </Link>{' '}
          to get started.
        </p>
      ) : (
        <div className="space-y-2 max-w-xl">
          {documents.slice(0, 5).map((doc) => (
            <div key={doc._id} className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg px-4 py-2">
              <span className="text-sm text-slate-200 truncate">{doc.title}</span>
              <span className="text-xs text-slate-500 capitalize">{doc.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
