# FILE: components/ChatWindow.jsx
// Main chat display component with auto-scroll and empty state

import React, { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

/**
 * ChatWindow - Main chat container component
 * 
 * Features:
 * - Displays all chat messages using MessageBubble
 * - Auto-scrolls to bottom on new messages
 * - Shows empty state with example prompts when no messages
 * - Full-height scrollable container
 * 
 * @param {Object} props
 * @param {Array} props.messages - Array of message objects
 * @param {Function} props.sendQuery - Callback to send example queries
 */
function ChatWindow({ messages, sendQuery }) {
  const messagesEndRef = useRef(null);

  /**
   * Auto-scroll to bottom when messages change
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Example prompts for empty state
  const examplePrompts = [
    "What are the latest AI breakthroughs in 2025?",
    "Explain quantum computing in simple terms",
    "What is the current state of nuclear fusion energy?"
  ];

  // Empty state
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-300 mb-2">
            Ask a question to start researching
          </h2>
          <p className="text-gray-500 text-sm">
            I'll search the web and provide comprehensive answers with sources
          </p>
        </div>
        
        <div className="space-y-2">
          {examplePrompts.map((prompt, index) => (
            <button
              key={index}
              onClick={() => sendQuery(prompt)}
              className="block w-full text-left px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors duration-200 border border-gray-700"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Messages display
  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      <div className="max-w-3xl mx-auto">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ChatWindow;
