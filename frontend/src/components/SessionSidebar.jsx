// Session Sidebar component for managing research sessions

import React from 'react';
import { X, MessageSquare, Plus, Save } from 'lucide-react';

/**
 * SessionSidebar - Sidebar component for session management
 *
 * Features:
 * - Display list of saved sessions
 * - Button to close/save current session
 * - Button to start new chat
 * - Shows current session status
 *
 * @param {Object} props
 * @param {Array} props.sessions - List of saved sessions
 * @param {number|null} props.currentSessionId - Current active session ID
 * @param {boolean} props.isLoading - Whether research is in progress
 * @param {Function} props.onCloseSession - Callback to close/save current session
 * @param {Function} props.onNewChat - Callback to start new chat
 * @param {Function} props.onLoadSession - Callback to load a saved session
 */
function SessionSidebar({
  sessions,
  currentSessionId,
  isLoading,
  onCloseSession,
  onNewChat,
  onLoadSession
}) {
  const hasActiveChat = currentSessionId !== null;

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateQuery = (query, maxLength = 30) => {
    if (!query) return 'Untitled Session';
    if (query.length <= maxLength) return query;
    return query.substring(0, maxLength) + '...';
  };

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Research Sessions
        </h2>
      </div>

      {/* Action Buttons */}
      <div className="p-4 space-y-2">
        {/* New Chat Button */}
        <button
          onClick={onNewChat}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>

        {/* Close & Save Session Button - only show when there's an active session */}
        {hasActiveChat && (
          <button
            onClick={onCloseSession}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Save className="w-4 h-4" />
            {isLoading ? 'Researching...' : 'Close & Save Session'}
          </button>
        )}
      </div>

      {/* Current Session Indicator */}
      {hasActiveChat && (
        <div className="px-4 py-2 bg-blue-900/30 border-y border-blue-800/50">
          <div className="flex items-center gap-2 text-blue-400 text-xs">
            <MessageSquare className="w-3 h-3" />
            <span>Active Session #{currentSessionId}</span>
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-1">
          {sessions.length === 0 ? (
            <p className="text-center text-gray-500 text-xs py-4">
              No saved sessions yet
            </p>
          ) : (
            sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onLoadSession?.(session.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors group ${
                  session.id === currentSessionId
                    ? 'bg-blue-900/50 border border-blue-700'
                    : 'hover:bg-gray-800 border border-transparent'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-300 font-medium truncate">
                      {truncateQuery(session.query)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(session.created_at)}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          session.status === 'completed'
                            ? 'bg-green-900/50 text-green-400'
                            : session.status === 'error'
                            ? 'bg-red-900/50 text-red-400'
                            : 'bg-yellow-900/50 text-yellow-400'
                        }`}
                      >
                        {session.status}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-800">
        <p className="text-xs text-gray-500">
          {sessions.length} saved session{sessions.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
}

export default SessionSidebar;
