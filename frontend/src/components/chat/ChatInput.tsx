'use client';

import { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = 'Type a message... (e.g., "Add buy groceries to my list")',
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-gradient-to-r from-gray-50 to-white p-4">
      <div className="flex items-end gap-3">
        <div className="flex-1 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 rounded-2xl blur opacity-20"></div>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="relative w-full resize-none rounded-2xl border-2 border-gray-200 bg-white px-5 py-4 pr-14 focus:border-purple-400 focus:ring-4 focus:ring-purple-100 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed text-sm transition-all duration-200 shadow-sm"
          />
          {/* Character count */}
          <div className="absolute right-4 bottom-2 text-xs text-gray-400">
            {message.length > 0 && `${message.length}`}
          </div>
        </div>
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="flex-shrink-0 bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 text-white rounded-2xl px-6 py-4 font-medium hover:from-purple-600 hover:via-pink-600 hover:to-blue-600 disabled:from-gray-300 disabled:via-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
        >
          {disabled ? (
            <div className="flex items-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span>Send</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-5 h-5"
              >
                <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
              </svg>
            </div>
          )}
        </button>
      </div>
      <div className="flex items-center justify-between mt-3">
        <p className="text-xs text-gray-500 flex items-center gap-1">
          <kbd className="px-2 py-0.5 bg-gray-100 rounded text-gray-600 font-mono text-xs">Enter</kbd>
          <span>to send</span>
          <span className="mx-1">•</span>
          <kbd className="px-2 py-0.5 bg-gray-100 rounded text-gray-600 font-mono text-xs">Shift + Enter</kbd>
          <span>for new line</span>
        </p>
        <div className="flex items-center gap-1 text-xs text-gray-400">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          <span>AI Ready</span>
        </div>
      </div>
    </form>
  );
}
