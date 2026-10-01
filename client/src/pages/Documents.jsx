import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Documents = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [title, setTitle] = useState('');
  const [file, setFile] = useState(null);
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/documents`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setDocuments(res.data);
      setError('');
    } catch (err) {
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        setError('Only PDF files are supported');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.replace('.pdf', ''));
      }
      setError('');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !title) {
      setError('Please provide a title and select a file');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);

    try {
      setUploading(true);
      setError('');
      await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${user.token}`
        }
      });
      setTitle('');
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/documents/${id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setDocuments(documents.filter(doc => doc._id !== id));
    } catch (err) {
      setError('Failed to delete document');
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Placeholder */}
      <div className="w-64 bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold mb-8">DevDocs AI</h1>
        <nav className="space-y-4">
          <Link to="/dashboard" className="block py-2 px-4 hover:bg-gray-800 rounded">Dashboard</Link>
          <Link to="/documents" className="block py-2 px-4 bg-gray-800 rounded">Documents</Link>
          <Link to="/chat" className="block py-2 px-4 hover:bg-gray-800 rounded">AI Chat</Link>
          <Link to="#" className="block py-2 px-4 hover:bg-gray-800 rounded">History</Link>
          <Link to="#" className="block py-2 px-4 hover:bg-gray-800 rounded">Settings</Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8 bg-gray-50">
        <h2 className="text-3xl font-semibold mb-6">Document Management</h2>
        
        {/* Upload Form */}
        <div className="bg-white p-6 rounded shadow mb-8">
          <h3 className="text-xl font-medium mb-4">Upload New Document (PDF)</h3>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <form onSubmit={handleUpload} className="flex gap-4 items-end flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input 
                type="text" 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., React Documentation"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-1">File</label>
              <input 
                type="file" 
                accept=".pdf"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="w-full border rounded px-3 py-1.5"
              />
            </div>
            <button 
              type="submit" 
              disabled={uploading || !file}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded disabled:opacity-50"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </form>
        </div>

        {/* Document List */}
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-xl font-medium mb-4">Your Documents</h3>
          {loading ? (
            <p>Loading documents...</p>
          ) : documents.length === 0 ? (
            <p className="text-gray-500">No documents uploaded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left">
                <thead className="border-b">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Title</th>
                    <th className="py-3 px-4 font-semibold">File Name</th>
                    <th className="py-3 px-4 font-semibold">Status</th>
                    <th className="py-3 px-4 font-semibold">Date</th>
                    <th className="py-3 px-4 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc._id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">{doc.title}</td>
                      <td className="py-3 px-4 text-gray-500">{doc.fileName}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          doc.status === 'completed' ? 'bg-green-100 text-green-800' : 
                          doc.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                          doc.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-sm">
                        {new Date(doc.createdAt).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button 
                          onClick={() => handleDelete(doc._id)}
                          className="text-red-500 hover:text-red-700"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Documents;
