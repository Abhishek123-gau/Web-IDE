import React, { useState, useEffect, useRef } from 'react';

const PreviewPane = ({ reloadKey }) => {
  const [loading, setLoading] = useState(false);
  const iframeRef = useRef(null);
  const appUrl = "http://localhost:5173/?mode=app";

  useEffect(() => {
    if (reloadKey > 0 && iframeRef.current) {
      setLoading(true);
      iframeRef.current.src = `${appUrl}&t=${Date.now()}`;
    }
  }, [reloadKey]);

  const handleRefresh = () => {
    setLoading(true);
    if (iframeRef.current) {
      iframeRef.current.src = `${appUrl}&t=${Date.now()}`;
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden transition-all duration-300">
      {/* Browser Chrome */}
      <div className="bg-slate-100 flex items-center p-3 gap-3 border-b border-slate-200">
        <div className="flex gap-1.5 pl-1">
          <div className="w-3 h-3 rounded-full bg-rose-400 shadow-inner"></div>
          <div className="w-3 h-3 rounded-full bg-amber-400 shadow-inner"></div>
          <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-inner"></div>
        </div>
        <div className="flex-1 flex gap-2">
          <button className="text-slate-400 hover:text-slate-600 p-1.5 rounded-md hover:bg-slate-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button className="text-slate-400 hover:text-slate-600 p-1.5 rounded-md hover:bg-slate-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button onClick={handleRefresh} className={`text-slate-400 hover:text-slate-600 p-1.5 rounded-md hover:bg-slate-200 transition-all ${loading ? 'animate-spin cursor-not-allowed text-blue-500' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <div className="flex-1 bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-600 flex items-center shadow-sm font-medium tracking-wide truncate">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 mr-2 text-slate-400 shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
            <span className="opacity-50 mr-0.5 shrink-0">https://</span>
            <span className="truncate">{appUrl}</span>
          </div>
        </div>
      </div>

      {/* Browser Viewport */}
      <div className="flex-1 bg-white relative overflow-hidden">
        {loading && (
          <div className="absolute inset-0 z-10 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center">
             <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
             <p className="text-slate-800 text-sm mt-4 font-bold shadow-sm">Refreshing Preview...</p>
          </div>
        )}
        <iframe 
          ref={iframeRef}
          src={appUrl} 
          title="App Preview"
          className="w-full h-full border-0"
          onLoad={() => setLoading(false)}
        />
      </div>
    </div>
  );
};

export default PreviewPane;
