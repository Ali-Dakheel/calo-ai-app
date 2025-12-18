/**
 * Chat Interface Component
 * Beautiful, smooth chat experience with AI agent
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import { useChatStore } from '@/lib/store';
import { formatTime, cn } from '@/lib/utils';

const CHAT_SUGGESTIONS = [
  'Show me high-protein meals',
  'I need vegan options',
  'Meals under 500 calories',
] as const;

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    userId,
    conversationId,
    addMessage,
    setLoading,
    setConversationId,
  } = useChatStore();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
    });

    setLoading(true);

    try {
      const response = await api.sendMessage({
        message: userMessage,
        user_id: userId,
        conversation_id: conversationId || undefined,
      });

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add AI response
      addMessage({
        role: 'assistant',
        content: response.message,
        agent: response.agent_used,
        recommendations: response.recommendations,
      });
    } catch (error) {
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again!',
      });
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleSuggestionKeyDown = (e: React.KeyboardEvent, suggestion: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setInput(suggestion);
    }
  };

  return (
    <div
      className="flex flex-col h-full bg-white rounded-2xl shadow-soft border border-gray-100"
      role="region"
      aria-label="Chat interface"
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-100">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-calo-primary to-green-600 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" aria-hidden="true" />
        </div>
        <div>
          <h2 className="font-semibold text-calo-dark">AI Nutrition Advisor</h2>
          <p className="text-sm text-gray-500">Ask me anything about meals!</p>
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-4"
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="text-center py-12 space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-calo-light flex items-center justify-center">
              <Bot className="w-8 h-8 text-calo-primary" aria-hidden="true" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-calo-dark mb-2">
                Welcome to Calo AI Advisor!
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                I can help you find the perfect meals based on your dietary preferences,
                nutritional goals, and taste preferences.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 pt-4" role="group" aria-label="Suggested questions">
              {CHAT_SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  onKeyDown={(e) => handleSuggestionKeyDown(e, suggestion)}
                  className="px-4 py-2 text-sm bg-calo-light text-calo-dark rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-calo-primary"
                  aria-label={`Ask: ${suggestion}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-3 animate-slide-up',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-calo-primary to-green-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" aria-hidden="true" />
              </div>
            )}

            <div
              className={cn(
                'max-w-[70%] rounded-2xl px-4 py-3',
                message.role === 'user'
                  ? 'bg-calo-primary text-white'
                  : 'bg-gray-50 text-calo-dark'
              )}
              role="article"
              aria-label={`${message.role === 'user' ? 'Your message' : 'AI response'}`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>

              {message.agent && (
                <p className="text-xs mt-2 opacity-60">
                  Agent: {message.agent.replace('_', ' ')}
                </p>
              )}

              <p
                className={cn(
                  'text-xs mt-2',
                  message.role === 'user' ? 'text-white/60' : 'text-gray-400'
                )}
              >
                {formatTime(message.timestamp)}
              </p>
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-calo-secondary flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-white" aria-hidden="true" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 animate-fade-in" aria-label="AI is typing">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-calo-primary to-green-600 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" aria-hidden="true" />
            </div>
            <div className="bg-gray-50 rounded-2xl px-4 py-3">
              <div className="flex gap-1 loading-dots" aria-hidden="true">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
              </div>
              <span className="sr-only">AI is thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about meals, nutrition, or your preferences..."
            className="flex-1 px-4 py-3 bg-gray-50 border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-calo-primary"
            disabled={isLoading}
            aria-label="Type your message"
            aria-describedby="chat-input-help"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={cn(
              'px-4 py-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-calo-primary',
              input.trim() && !isLoading
                ? 'bg-calo-primary text-white hover:bg-green-600 hover:shadow-glow-green'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            )}
            aria-label="Send message"
          >
            <Send className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>
        <p id="chat-input-help" className="sr-only">
          Press Enter to send your message
        </p>
      </div>
    </div>
  );
};
