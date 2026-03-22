# FILE: components/MessageBubble.jsx
// Component for rendering individual chat messages with markdown support

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceCard from './SourceCard';

/**
 * MessageBubble - Renders a single chat message
 * 
 * User messages: Right-aligned blue bubbles
 * Assistant messages: Left-aligned with markdown rendering, typing indicators, and status
 * 
 * @param {Object} props
 * @param {Object} props.message - Message object with role, content, status, sources
 */
function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-600 text-white rounded-2xl px-4 py-2 max-w-[80%]">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-4">
      <div className="w-full max-w-[90%]">
        {/* Status indicator */}
        {message.status && (
          <div className="text-gray-400 text-sm mb-2 flex items-center">
            <span className="inline-flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
              {message.status}
            </span>
          </div>
        )}
        
        {/* Message content */}
        <div className="text-gray-100 prose prose-invert prose-sm max-w-none">
          {message.content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          ) : (
            /* Typing indicator */
            <div className="flex items-center space-x-1 text-gray-400">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          )}
        </div>
        
        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <SourceCard sources={message.sources} />
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
