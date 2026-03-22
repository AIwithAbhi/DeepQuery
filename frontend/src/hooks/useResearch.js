// Custom React hook for managing research chat state and API communication

import { useState, useCallback, useRef } from 'react';

/**
 * useResearch - Custom hook for the AI Research Agent chat functionality
 *
 * Manages message state, loading status, session tracking, and handles streaming responses
 * from the backend API via Server-Sent Events (SSE).
 *
 * @returns {Object} - { messages, isLoading, currentSessionId, sessions, sendQuery, closeSession, loadSessions, clearMessages }
 */
export function useResearch() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const abortControllerRef = useRef(null);

  /**
   * Load all sessions from the backend
   */
  const loadSessions = useCallback(async () => {
    try {
      const response = await fetch('/api/sessions');
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  }, []);

  /**
   * Close the current session and save it to database
   */
  const closeSession = useCallback(async () => {
    if (!currentSessionId || messages.length === 0) return;

    try {
      // Compile the full conversation
      const conversation = messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: new Date().toISOString()
      }));

      // Save session to backend
      const response = await fetch(`/api/sessions/${currentSessionId}/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: conversation,
          query: messages[0]?.content || 'Research Session'
        })
      });

      if (response.ok) {
        setCurrentSessionId(null);
        setMessages([]);
        await loadSessions(); // Refresh sessions list
      }
    } catch (error) {
      console.error('Error closing session:', error);
    }
  }, [currentSessionId, messages, loadSessions]);

  /**
   * Clear current messages without saving (new chat)
   */
  const clearMessages = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setMessages([]);
    setCurrentSessionId(null);
  }, []);

  /**
   * Send a research query to the backend and process the streaming response
   * @param {string} query - The user's research question
   */
  const sendQuery = useCallback(async (query) => {
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
      status: null,
      sources: null
    };

    // Add empty assistant message
    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      status: 'thinking',
      sources: null
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      // Send request to backend
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let receivedSessionId = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              // Capture session ID from done message
              if (data.type === 'done' && data.session_id) {
                receivedSessionId = data.session_id;
                setCurrentSessionId(data.session_id);
              }

              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];

                if (data.type === 'status') {
                  // Update status
                  lastMessage.status = data.text;
                } else if (data.type === 'text') {
                  // Append text to content
                  lastMessage.content += data.text;
                  lastMessage.status = null;
                } else if (data.type === 'done') {
                  // Complete the message
                  lastMessage.status = null;
                  setIsLoading(false);
                } else if (data.type === 'error') {
                  // Handle error
                  lastMessage.content = `Error: ${data.text}`;
                  lastMessage.status = null;
                  setIsLoading(false);
                }

                return newMessages;
              });

              if (data.type === 'done' || data.type === 'error') {
                setIsLoading(false);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }

      // Auto-save to session after completion
      if (receivedSessionId) {
        setCurrentSessionId(receivedSessionId);
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
        return;
      }
      console.error('Error sending query:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        lastMessage.content = `Error: ${error.message}`;
        lastMessage.status = null;
        return newMessages;
      });
      setIsLoading(false);
    }
  }, []);

  return {
    messages,
    isLoading,
    currentSessionId,
    sessions,
    sendQuery,
    closeSession,
    loadSessions,
    clearMessages
  };
}
