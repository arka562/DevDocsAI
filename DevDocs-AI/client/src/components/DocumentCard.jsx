import React from 'react';
import { FileText, Trash2, Loader2, CheckCircle2, XCircle } from 'lucide-react';

const statusConfig = {
  uploaded: { label: 'Queued', icon: Loader2, color: 'text-slate-400' },
  processing: { label: 'Processing', icon: Loader2, color: 'text-amber-400' },
  completed: { label: 'Ready', icon: CheckCircle2, color: 'text-emerald-400' },
  failed: { label: 'Failed', icon: XCircle, color: 'text-red-400' }
};

const DocumentCard = ({ doc, onDelete }) => {
  const status = statusConfig[doc.status] || statusConfig.uploaded;
  const StatusIcon = status.icon;

  return (
    <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl px-4 py-3">
      <div className="flex items-center gap-3 min-w-0">
        <FileText className="text-indigo-400 shrink-0" size={20} />
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-100 truncate">{doc.title}</p>
          <p className="text-xs text-slate-500">
            {doc.status === 'completed' ? `${doc.chunkCount} chunks` : status.label}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <span className={`flex items-center gap-1 text-xs ${status.color}`}>
          <StatusIcon size={14} className={doc.status === 'processing' ? 'animate-spin' : ''} />
          {status.label}
        </span>
        <button onClick={() => onDelete(doc._id)} className="text-slate-500 hover:text-red-400">
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

export default DocumentCard;
