'use client';

import { useState, useEffect, useRef } from 'react';
import { Message, Conversation } from '@/types';
import {
  sendChatMessage,
  fetchConversations,
  getConversation,
  deleteConversation,
} from '@/lib/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      setIsLoadingHistory(true);
      const data = await fetchConversations();
      setConversations(data);

      // If there are conversations, load the most recent one
      if (data.length > 0) {
        await loadConversation(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const data = await getConversation(conversationId);
      setCurrentConversationId(conversationId);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load conversation:', err);
      setError('Failed to load conversation');
    }
  };

  const startNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));

      if (currentConversationId === id) {
        startNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message optimistically
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: currentConversationId || '',
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await sendChatMessage({
        message: content,
        conversation_id: currentConversationId || undefined,
      });

      // Update conversation ID if new
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        // Refresh conversations list
        loadConversations();
      }

      // Replace temp message with real one and add assistant response
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id);
        return [...filtered, response.message, response.assistant_message];
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      // Remove the temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-140px)] bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
      {/* Sidebar */}
      <div className="w-72 bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 flex flex-col">
        {/* Sidebar Header */}
        <div className="p-5 border-b border-white/10">
          <button
            onClick={startNewChat}
            className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 text-white rounded-xl py-3 px-4 font-semibold hover:from-purple-600 hover:via-pink-600 hover:to-blue-600 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-5 h-5"
            >
              <path
                fillRule="evenodd"
                d="M12 3.75a.75.75 0 0 1 .75.75v6.75h6.75a.75.75 0 0 1 0 1.5h-6.75v6.75a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z"
                clipRule="evenodd"
              />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto py-3 px-3">
          <div className="text-xs font-semibold text-purple-300 uppercase tracking-wider mb-3 px-2">
            Recent Chats
          </div>
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-gray-400 text-sm">
              <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                </svg>
              </div>
              <p>No conversations yet</p>
              <p className="text-xs text-gray-500 mt-1">Start a new chat!</p>
            </div>
          ) : (
            <div className="space-y-1">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`group flex items-center rounded-xl cursor-pointer transition-all duration-200 ${
                    currentConversationId === conv.id
                      ? 'bg-gradient-to-r from-purple-500/30 to-pink-500/30 border border-purple-400/30'
                      : 'hover:bg-white/5'
                  }`}
                >
                  <button
                    onClick={() => loadConversation(conv.id)}
                    className="flex-1 text-left px-4 py-3 truncate text-sm text-gray-200 flex items-center gap-3"
                  >
                    <span className="text-lg">💬</span>
                    <span className="truncate">{conv.title || 'New Chat'}</span>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conv.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-2 mr-2 text-gray-400 hover:text-red-400 transition-all rounded-lg hover:bg-red-500/10"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      className="w-4 h-4"
                    >
                      <path
                        fillRule="evenodd"
                        d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.519.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5Z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center gap-3 text-gray-400 text-xs">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <span className="text-white text-sm">🤖</span>
            </div>
            <div>
              <div className="text-gray-200 font-medium">Todo AI</div>
              <div className="text-gray-500">Powered by GPT-4</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-50 via-white to-purple-50/30">
        {/* Chat Header */}
        <div className="border-b border-gray-100 px-8 py-5 bg-white/80 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 flex items-center justify-center shadow-lg">
              <span className="text-2xl">✨</span>
            </div>
            <div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                Todo AI Assistant
              </h2>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Online • Ready to help manage your tasks
              </p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {messages.length === 0 && !isLoading ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-3xl flex items-center justify-center mb-6 shadow-2xl animate-pulse">
                <span className="text-5xl">🚀</span>
              </div>
              <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-3">
                Welcome to Todo AI!
              </h3>
              <p className="text-gray-500 max-w-md mb-8">
                I&apos;m your personal AI assistant. Tell me what you need to do and I&apos;ll help you manage your tasks effortlessly.
              </p>
              <div className="grid grid-cols-2 gap-3 max-w-lg">
                {[
                  { icon: '📝', text: 'Add buy groceries to my list' },
                  { icon: '📋', text: 'Show me my tasks' },
                  { icon: '✅', text: 'Mark groceries as done' },
                  { icon: '🗑️', text: 'Delete all completed tasks' },
                ].map((example, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendMessage(example.text)}
                    className="bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-700 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 flex items-center gap-2 text-left shadow-sm hover:shadow-md"
                  >
                    <span className="text-lg">{example.icon}</span>
                    <span className="truncate">{example.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {/* Streaming message */}
              {streamingMessage && (
                <div className="flex justify-start mb-4">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center shadow-lg">
                      <span className="text-white">🤖</span>
                    </div>
                  </div>
                  <div className="max-w-[75%] rounded-2xl px-5 py-4 bg-white border border-gray-100 text-gray-800 rounded-bl-sm shadow-md">
                    <div className="text-xs font-semibold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
                      🤖 AI Assistant
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {streamingMessage}
                      <span className="inline-block w-2 h-4 bg-purple-400 ml-1 animate-pulse rounded" />
                    </div>
                  </div>
                </div>
              )}

              {/* Loading indicator */}
              {isLoading && !streamingMessage && (
                <div className="flex justify-start mb-4">
                  <div className="flex-shrink-0 mr-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 flex items-center justify-center shadow-lg animate-pulse">
                      <span className="text-white">🤖</span>
                    </div>
                  </div>
                  <div className="bg-white border border-gray-100 rounded-2xl px-5 py-4 rounded-bl-sm shadow-md">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-1">
                        <span className="w-2.5 h-2.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2.5 h-2.5 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                      <span className="text-sm text-gray-500">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="mx-8 mb-3 p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center gap-3 shadow-sm">
            <span className="text-xl">⚠️</span>
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600"
            >
              ✕
            </button>
          </div>
        )}

        {/* Input */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
