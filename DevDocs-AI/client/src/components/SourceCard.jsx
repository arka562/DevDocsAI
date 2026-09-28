import React from 'react';
import { FileText } from 'lucide-react';

const SourceCard = ({ source }) => (
  <div className="bg-slate-800/60 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-300">
    <div className="flex items-center gap-2 font-medium text-slate-200 mb-1">
      <FileText size={14} className="text-indigo-400" />
      {source.document_name}
    </div>
    <p className="text-slate-400 line-clamp-2">{source.text}</p>
  </div>
);

export default SourceCard;
