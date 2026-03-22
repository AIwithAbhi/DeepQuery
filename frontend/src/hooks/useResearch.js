 
// Custom React hook for managing research chat state and API communication

import { useState, useCallback } from 'react';

/**
 * useResearch - Custom hook for the AI Research Agent chat functionality
 * 
 * Manages message state, loading status, and handles streaming responses
 * from the backend API via Server-Sent Events (SSE).
 * 
 * @returns {Object} - { messages, isLoading, sendQuery }
 */
export function useResearch() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

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

    try {
      // Send request to backend
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
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
    } catch (error) {
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

  return { messages, isLoading, sendQuery };
}
