import { useState, useCallback, useRef, useEffect } from 'react';
import { Message, MentorResponse } from '../types/chat';
import { apiClient, fetchWithBackoff, ApiError } from '../api/chat';
import { v4 as uuidv4 } from 'uuid';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => localStorage.getItem('mentor_session') || uuidv4());
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
      const data = await fetchWithBackoff(() =>
        apiClient<MentorResponse>(`${baseUrl}/api/v1/chat`, {
          method: 'POST',
          body: JSON.stringify({ message: text, session_id: sessionId }),
          signal: abortControllerRef.current?.signal
        })
      );
      const assistantMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: data,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMsg]);
      localStorage.setItem('mentor_session', sessionId);
      
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      
      const message = err instanceof ApiError 
        ? `Mentor is currently unavailable (${err.status}).` 
        : "Failed to connect to the mentor.";
      
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    return () => abortControllerRef.current?.abort();
  }, []);

  return { messages, isLoading, error, sendMessage };
};
