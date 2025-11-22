"use client";
import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { Citation } from '@/types';
import MessageBubble from './MessageBubble';

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
}

interface ChatInterfaceProps {
  uploadId: string;
}

export default function ChatInterface({ uploadId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: 'intro', role: 'ai', content: 'I have analyzed your document. What would you like to know?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.askQuestion(uploadId, userMsg.content);
      if (response.data) {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: response.data.answer,
          citations: response.data.citations
        };
        setMessages(prev => [...prev, aiMsg]);
      }
    } catch (error) {
      console.error(error);
      const errorMsg: Message = { 
        id: Date.now().toString(), 
        role: 'ai', 
        content: "Sorry, I encountered an error getting the answer." 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-white border-b border-gray-100 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-500/20">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 text-sm">Document Assistant</h3>
          <p className="text-xs text-gray-500">Ask questions about your file</p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} {...msg} />
        ))}
        
        {isLoading && (
          <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm flex gap-1.5 items-center">
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-100">
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            // FIX: Added text-gray-900 to make text visible
            className="w-full pl-5 pr-12 py-3.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 focus:bg-white transition-all outline-none text-sm text-gray-900 placeholder:text-gray-400 shadow-sm"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md active:scale-95"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
        <p className="text-[10px] text-gray-400 mt-2 text-center">
          AI generated responses can be inaccurate.
        </p>
      </div>
    </div>
  );
}