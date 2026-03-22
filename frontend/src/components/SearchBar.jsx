# FILE: components/SearchBar.jsx
// Component for the chat input with send button

import React, { useState } from 'react';
import { Send } from 'lucide-react';

/**
 * SearchBar - Input component for submitting research queries
 * 
 * Features:
 * - Full-width text input
 * - Send button with loading state
 * - Enter key submission
 * - Disabled state while loading
 * 
 * @param {Object} props
 * @param {Function} props.onSubmit - Callback when user submits query
 * @param {boolean} props.isLoading - Whether the agent is processing
 */
function SearchBar({ onSubmit, isLoading }) {
  const [inputValue, setInputValue] = useState('');

  /**
   * Handle form submission
   * @param {Event} e - Form submit event
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim());
      setInputValue('');
    }
  };

  /**
   * Handle Enter key press
   * @param {KeyboardEvent} e - Keyboard event
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-center space-x-2 bg-gray-800 rounded-full px-4 py-2 border border-gray-700 focus-within:border-blue-500 transition-colors">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything to research..."
          disabled={isLoading}
          className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none text-sm py-1 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-full transition-colors duration-200"
        >
          <Send className="w-4 h-4 text-white" />
        </button>
      </div>
    </form>
  );
}

export default SearchBar;
