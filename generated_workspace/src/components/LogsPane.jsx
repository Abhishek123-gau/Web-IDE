import React, { useEffect, useState, useRef } from 'react';

const LogsPane = () => {
  const [logs, setLogs] = useState([
    "[SYSTEM] Connecting to local agent stream..."
  ]);
  const logsEndRef = useRef(null);
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Detect manual scroll
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    // If user scrolled up (more than 50px away from bottom), disable auto-scroll
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/api/logs');

    eventSource.onopen = () => {
      setLogs(prev => [...prev, "[SUCCESS] Connected to live agent trace."]);
    };

    eventSource.onmessage = (event) => {
      if (event.data) {
        try {
          // Server sends raw stdout chunks encoded as json {"chunk": "..."}
          const payload = JSON.parse(event.data);
          const chunk = payload.chunk;
          
          setLogs(prev => {
            if (prev.length === 0) return [chunk];
            
            // If the chunk contains a newline, split it up
            if (chunk.includes('\n')) {
               const parts = chunk.split('\n');
               const newLogs = [...prev];
               
               // Append the first part to the last line
               newLogs[newLogs.length - 1] += parts[0];
               
               // Push the rest as new lines
               for (let i = 1; i < parts.length; i++) {
                 // Push everything, even empty string, to create true blank lines
                 newLogs.push(parts[i]); 
               }
               
               if (newLogs.length > 250) return newLogs.slice(newLogs.length - 250);
               return newLogs;
            } else {
               // Append purely to the last line without breaking
               const newLogs = [...prev];
               newLogs[newLogs.length - 1] += chunk;
               return newLogs;
            }
          });
        } catch (e) {
          // Fallback if not JSON
          setLogs(prev => {
             const newLogs = [...prev, event.data];
             if (newLogs.length > 250) return newLogs.slice(newLogs.length - 250);
             return newLogs;
          });
        }
      }
    };

    eventSource.onerror = (error) => {
      console.log('SSE connection error, retrying in background...');
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    if (autoScroll) {
      // Changed to 'auto' to prevent jarring skips during rapid events
      logsEndRef.current?.scrollIntoView({ behavior: "auto" });
    }
  }, [logs, autoScroll]);

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e] rounded-2xl border border-slate-700/50 shadow-xl overflow-hidden font-mono text-xs relative">
      {/* Scroll to bottom button if user scrolled up */}
      {!autoScroll && (
        <button 
          onClick={() => {
             setAutoScroll(true);
             logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
          }}
          className="absolute bottom-6 right-6 bg-slate-700/80 hover:bg-slate-600/80 text-emerald-400 p-2 rounded-full shadow-lg backdrop-blur-sm transition-all z-20 border border-slate-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      )}
      <div className="p-3 bg-[#252526] border-b border-black/50 flex items-center justify-between shadow-sm z-10 shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-semibold tracking-wider">AGENT TRACE</span>
          <span className="flex items-center gap-1.5 text-emerald-500/90 text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 uppercase tracking-widest font-bold">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
            Live
          </span>
        </div>
        <div className="flex gap-1.5">
          <svg className="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-pointer transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </div>
      </div>
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 p-4 overflow-y-auto space-y-0 custom-scrollbar text-emerald-400/90 tracking-wide bg-[#1e1e1e] break-before-avoid relative"
      >
        {logs.map((log, index) => {
          // Slight styling adjustments based on keywords
          const isError = log.includes('[ERROR]') || log.includes('❌') || log.toLowerCase().includes('traceback') || log.toLowerCase().includes('error');
          const isSuccess = log.includes('[SUCCESS]') || log.includes('✅');
          const isSystem = log.includes('[SYSTEM]') || log.includes('🤖') || log.includes('[Agent Updates]');
          const isWarning = log.includes('[WARN]') || log.includes('Warning');

          const colorClass = isSuccess ? 'text-blue-400 font-medium' :
                             isWarning ? 'text-amber-400' : 
                             isError ? 'text-rose-400 font-medium' :
                             isSystem ? 'text-purple-400 font-medium' : 'text-slate-300';
                             
          // Ensure zero-height lines for pure empty strings so spacing doesn't get huge
          if (log === '') {
             return <div key={index} className="h-2"></div>;
          }

          return (
            <div key={index} className="flex gap-3 hover:bg-white/5 px-2 py-0.5 rounded transition-colors text-[11px] leading-relaxed">
              <span className="text-slate-600 shrink-0 select-none opacity-50 mt-0.5">{`>_`}</span>
              <span className={`flex-1 whitespace-pre-wrap break-words ${colorClass}`}>
                {log}
              </span>
            </div>
          );
        })}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default LogsPane;
