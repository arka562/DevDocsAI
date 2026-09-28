import React from 'react';
import ReactMarkdown from 'react-markdown';
import SourceCard from './SourceCard.jsx';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
      <span className="text-xs text-slate-500 mb-1">{isUser ? 'You' : 'DevDocs AI'}</span>
      <div
        className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-100'
        }`}
      >
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>

      {!isUser && message.sources?.length > 0 && (
        <div className="mt-2 grid gap-2 max-w-2xl w-full">
          {message.sources.map((s, i) => (
            <SourceCard key={i} source={s} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
