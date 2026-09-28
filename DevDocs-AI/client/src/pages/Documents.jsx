import React, { useEffect, useState, useRef } from 'react';
import { Upload } from 'lucide-react';
import api from '../services/api';
import DocumentCard from '../components/DocumentCard.jsx';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const fetchDocuments = () => {
    api.get('/documents').then((res) => setDocuments(res.data));
  };

  useEffect(() => {
    fetchDocuments();
    // Poll every 4s so "processing" -> "completed" status updates without
    // a manual refresh. Simple approach, good enough for an MVP.
    const interval = setInterval(fetchDocuments, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError('');
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.replace(/\.pdf$/i, ''));

    try {
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.message || 'Upload failed');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (id) => {
    await api.delete(`/documents/${id}`);
    setDocuments((prev) => prev.filter((d) => d._id !== id));
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Documents</h2>
        <label className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium cursor-pointer transition">
          <Upload size={16} />
          {uploading ? 'Uploading...' : 'Upload PDF'}
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      {documents.length === 0 ? (
        <p className="text-sm text-slate-500">Upload a PDF to start building your knowledge base.</p>
      ) : (
        <div className="space-y-2 max-w-2xl">
          {documents.map((doc) => (
            <DocumentCard key={doc._id} doc={doc} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Documents;
