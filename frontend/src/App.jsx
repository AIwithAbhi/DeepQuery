// Main application component - Layout and state management

import React, { useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import SearchBar from './components/SearchBar';
import SessionSidebar from './components/SessionSidebar';
import { useResearch } from './hooks/useResearch';

/**
 * App - Root component for the AI Research Agent
 *
 * Layout:
 * - SessionSidebar on the left for managing sessions
 * - Main chat area with ChatWindow and SearchBar
 * - Dark theme styling
 */
function App() {
  const {
    messages,
    isLoading,
    currentSessionId,
    sessions,
    sendQuery,
    closeSession,
    loadSessions,
    clearMessages
  } = useResearch();

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleLoadSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        // Convert session data to messages format
        const sessionMessages = [];
        if (data.query) {
          sessionMessages.push({
            id: Date.now(),
            role: 'user',
            content: data.query,
            status: null,
            sources: null
          });
        }
        if (data.response) {
          sessionMessages.push({
            id: Date.now() + 1,
            role: 'assistant',
            content: data.response,
            status: null,
            sources: data.search_results?.[0]?.results || null
          });
        }
        // Update messages and set current session
        // Note: This would need state setter exposed from hook
        console.log('Loading session:', data);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  return (
    <div className="h-screen flex bg-gray-950 text-white overflow-hidden">
      {/* Session Sidebar */}
      <SessionSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        isLoading={isLoading}
        onCloseSession={closeSession}
        onNewChat={clearMessages}
        onLoadSession={handleLoadSession}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex-shrink-0">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-white">AI Research Agent</h1>
              <p className="text-xs text-gray-500 mt-1">
                Powered by Kimi K2.5 + Brave Search
              </p>
            </div>
            {currentSessionId && (
              <div className="text-xs text-blue-400 bg-blue-900/30 px-3 py-1 rounded-full">
                Session #{currentSessionId}
              </div>
            )}
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
    </div>
  );
}

export default App;
