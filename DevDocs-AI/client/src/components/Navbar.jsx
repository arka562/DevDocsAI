import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, FileText, MessageSquare, LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const linkClass = ({ isActive }) =>
  `flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition ${
    isActive ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
  }`;

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-60 shrink-0 border-r border-slate-800 bg-slate-900 flex flex-col">
      <div className="px-5 py-5 border-b border-slate-800">
        <h1 className="text-lg font-bold text-white">DevDocs AI</h1>
        {user && <p className="text-xs text-slate-500 mt-1 truncate">{user.name}</p>}
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        <NavLink to="/" end className={linkClass}>
          <LayoutDashboard size={18} /> Dashboard
        </NavLink>
        <NavLink to="/documents" className={linkClass}>
          <FileText size={18} /> Documents
        </NavLink>
        <NavLink to="/chat" className={linkClass}>
          <MessageSquare size={18} /> AI Chat
        </NavLink>
      </nav>

      <button
        onClick={handleLogout}
        className="m-3 flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800 hover:text-red-400 transition"
      >
        <LogOut size={18} /> Logout
      </button>
    </aside>
  );
};

export default Navbar;
