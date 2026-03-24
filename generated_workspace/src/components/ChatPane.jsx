import React, { useState, useEffect, useRef } from 'react';

const ChatPane = ({ onCodeGenerated }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Welcome to Nexus IDE! How can I help you today?", sender: "ai" }
  ]);
  const [historyStrings, setHistoryStrings] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, autoScroll]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { id: Date.now(), text: userMsg, sender: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          message: userMsg,
          chat_history: historyStrings
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      const data = await response.json();
      setHistoryStrings(data.chat_history || []);
      
      if (data.build_error) {
        setMessages(prev => [...prev, { id: Date.now(), text: `Generation failed with error: ${data.build_error}`, sender: 'ai', error: true }]);
      } else {
        setMessages(prev => [...prev, { id: Date.now(), text: "I have processed your request and updated the workspace. The view should reload shortly.", sender: 'ai' }]);
        if (onCodeGenerated) onCodeGenerated();
      }
    } catch (error) {
       console.error("Chat API Error:", error);
       setMessages(prev => [...prev, { id: Date.now(), text: `Connection Error: Make sure the FastAPI backend (localhost:8000) is running.`, sender: 'ai', error: true }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-800/80 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden relative">
      {!autoScroll && (
        <button 
          onClick={() => {
             setAutoScroll(true);
             messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
          }}
          className="absolute bottom-24 right-6 bg-blue-600/80 hover:bg-blue-500 text-white p-2 rounded-full shadow-lg backdrop-blur-sm transition-all z-20"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      )}
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50 bg-slate-800/50 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          AI Dev
        </h2>
        {loading && <span className="text-xs text-blue-400 animate-pulse">Agent processing...</span>}
      </div>

      {/* Messages Area */}
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 p-4 overflow-y-auto space-y-4 filter drop-shadow-sm custom-scrollbar relative"
      >
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-sm' 
                : msg.error 
                  ? 'bg-red-900/50 text-red-200 border border-red-700/50 rounded-tl-sm'
                  : 'bg-slate-700/80 text-slate-200 rounded-tl-sm border border-slate-600/50'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed bg-slate-700/80 text-slate-200 rounded-tl-sm border border-slate-600/50 flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-slate-800/50 border-t border-slate-700/50">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder={loading ? "Waiting for agent to finish..." : "Type your request (e.g., 'Make the button green')..."}
            className="w-full bg-slate-900/50 border border-slate-600/50 rounded-xl py-3 pl-4 pr-12 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all text-sm shadow-inner disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg transition-colors shadow-md"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPane;
