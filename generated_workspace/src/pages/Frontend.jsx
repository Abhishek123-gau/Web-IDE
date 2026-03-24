import React, { useState } from 'react';
import ChatPane from '../components/ChatPane';
import LogsPane from '../components/LogsPane';
import PreviewPane from '../components/PreviewPane';

const Frontend = () => {
  const [reloadKey, setReloadKey] = useState(0);

  const handleCodeGenerated = () => {
    // Incrementing this key will trigger the iframe in PreviewPane to reload
    setReloadKey(prev => prev + 1);
  };

  return (
    <div className="h-screen w-full bg-[#0B0F19] p-4 font-sans text-slate-100 flex flex-col overflow-hidden relative selection:bg-blue-500/30">
      {/* Dynamic Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[30vw] h-[30vw] bg-purple-600/20 blur-[120px] rounded-full pointer-events-none mix-blend-screen"></div>

      {/* Header */}
      <header className="flex justify-between items-center mb-5 px-2 z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 p-2 rounded-xl shadow-lg shadow-blue-500/30 border border-blue-400/20">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">Nexus IDE</h1>
            <p className="text-[10px] uppercase font-bold tracking-widest text-blue-400/80">Autonomous Mode</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm font-medium">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full text-green-400 text-xs">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
            System Online
          </div>
          <button className="px-4 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/50 transition-all backdrop-blur-md">
            Environment
          </button>
          <button 
            onClick={() => window.open('http://localhost:5173/?mode=app', '_blank')}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 transition-all border border-indigo-400/20">
            Open App Fullscreen
          </button>
          <button className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25 transition-all border border-blue-400/20">
            Deploy App
          </button>
        </div>
      </header>

      {/* Main 3-Pane Layout Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 z-10 min-h-0">
        
        {/* Left Pane: Chat */}
        <div className="col-span-1 lg:col-span-3 h-full min-h-0 animate-in fade-in slide-in-from-left-4 duration-500">
          <ChatPane onCodeGenerated={handleCodeGenerated} />
        </div>

        {/* Middle Pane: Console / Streaming */}
        <div className="col-span-1 lg:col-span-4 h-full min-h-0 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100">
          <LogsPane />
        </div>

        {/* Right Pane: Website Preview */}
        <div className="col-span-1 lg:col-span-5 h-full min-h-0 animate-in fade-in slide-in-from-right-4 duration-500 delay-200">
          <PreviewPane reloadKey={reloadKey} />
        </div>
        
      </div>
    </div>
  );
};

export default Frontend;
