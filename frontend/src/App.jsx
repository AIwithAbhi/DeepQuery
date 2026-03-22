# FILE: App.jsx
// Main application component - Layout and state management

import React from 'react';
import ChatWindow from './components/ChatWindow';
import SearchBar from './components/SearchBar';
import { useResearch } from './hooks/useResearch';

/**
 * App - Root component for the AI Research Agent
 * 
 * Layout:
 * - Full viewport height flex column
 * - Header with title and subtitle
 * - ChatWindow (flex-grow, scrollable message area)
 * - SearchBar (sticky bottom input)
 * - Dark theme styling
 */
function App() {
  const { messages, isLoading, sendQuery } = useResearch();

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white overflow-hidden">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex-shrink-0">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-xl font-bold text-white">AI Research Agent</h1>
          <p className="text-xs text-gray-500 mt-1">
            Powered by Claude + Brave Search
          </p>
        </div>
      </header>

      {/* Chat Window */}
      <ChatWindow messages={messages} sendQuery={sendQuery} />

      {/* Search Bar */}
      <div className="border-t border-gray-800 bg-gray-900 px-6 py-4 flex-shrink-0">
        <div className="max-w-3xl mx-auto">
          <SearchBar onSubmit={sendQuery} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;
