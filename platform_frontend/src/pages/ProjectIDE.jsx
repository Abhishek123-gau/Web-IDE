import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Terminal, Code2, LayoutTemplate } from 'lucide-react'
import api from '../api'

export default function ProjectIDE() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [projectTitle, setProjectTitle] = useState("Loading...")
  const [chatHistory, setChatHistory] = useState([])
  const [input, setInput] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [logs, setLogs] = useState([])
  const [iframeKey, setIframeKey] = useState(0) // Forces iframe refresh
  
  const chatEndRef = useRef(null)
  const logsEndRef = useRef(null)

  // 1. Initial Load: Sync database to workspace filesystem & fetch history
  useEffect(() => {
    const init = async () => {
      try {
        // Fetch project metadata
        const { data: allProjects } = await api.get('/projects/')
        const proj = allProjects.find(p => p.id === parseInt(id))
        if (proj) {
          setProjectTitle(proj.title)
          try {
            setChatHistory(JSON.parse(proj.chat_history))
          } catch(e) {}
        }
        
        // Load physical files directly into the Vite target directory
        await api.post(`/projects/${id}/load`)
        // Force iframe to reload to pick up instantly dumped files
        setIframeKey(k => k + 1)
      } catch (err) {
        console.error("Failed to load project", err)
      }
    }
    init()
  }, [id])

  // 2. Setup Server-Sent Events (SSE) for Real-time LLM reasoning logs
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/api/logs')
    eventSource.onmessage = (event) => {
      const parsed = JSON.parse(event.data)
      setLogs(prev => [...prev, parsed.chunk])
    }
    return () => eventSource.close()
  }, [])

  // Auto-scroll
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [chatHistory])
  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [logs])

  // 3. Handle Chat Submission
  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isGenerating) return
    
    // Optimistic UI
    const tempMsg = `User: ${input}`
    setChatHistory(prev => [...prev, tempMsg])
    setInput("")
    setIsGenerating(true)
    setLogs(prev => [...prev, `\n\n--- Starting Generation for: "${tempMsg}" ---\n`])
    
    try {
      // Chat endpoint invokes LangGraph, writes files, and persists SQLite seamlessly
      const { data } = await api.post('/chat', { project_id: parseInt(id), message: input })
      setChatHistory(data.chat_history)
      // Vite Hot Module Replacement automatically injects changes into the iframe!
    } catch (err) {
      console.error(err)
      setLogs(prev => [...prev, "\n[ERROR]: Failed to connect to AI Agent."])
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-300 font-sans overflow-hidden">
      
      {/* ----------------- Pane 1: Chat Interface (25%) ----------------- */}
      <div className="w-1/4 min-w-[300px] border-r border-slate-800 flex flex-col bg-slate-900">
        <header className="p-4 border-b border-slate-800 flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="hover:text-white transition-colors">
            <ArrowLeft size={20} />
          </button>
          <h2 className="font-bold text-white truncate"><LayoutTemplate size={16} className="inline mr-2 text-blue-400"/> {projectTitle}</h2>
        </header>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chatHistory.length === 0 && (
            <p className="text-slate-500 text-sm text-center mt-10">Describe the UI you want to build.</p>
          )}
          {chatHistory.map((msg, i) => {
            const isUser = msg.startsWith("User:")
            return (
              <div key={i} className={`p-3 rounded-xl text-sm ${isUser ? 'bg-blue-600/20 text-blue-100 border border-blue-500/30 ml-4' : 'bg-slate-800 text-slate-200 border border-slate-700 mr-4'}`}>
                {msg.replace("User: ", "").replace("System Plan:\\n", "")}
              </div>
            )
          })}
          <div ref={chatEndRef} />
        </div>
        
        <form onSubmit={handleSend} className="p-4 bg-slate-900 border-t border-slate-800">
          <div className="relative flex items-center">
            <input 
              value={input} 
              onChange={e => setInput(e.target.value)}
              placeholder="E.g. Add a hero section..."
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-4 pr-12 py-3 text-sm focus:outline-none focus:border-blue-500 transition-colors"
              disabled={isGenerating}
            />
            <button 
              type="submit" 
              disabled={isGenerating || !input.trim()}
              className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md disabled:opacity-50 transition-colors"
            >
              {isGenerating ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send size={16} />}
            </button>
          </div>
        </form>
      </div>

      {/* ----------------- Pane 2: Agent Reasoning Logs (25%) ----------------- */}
      <div className="w-1/4 min-w-[300px] border-r border-slate-800 bg-black flex flex-col font-mono text-xs">
        <header className="p-2 border-b border-slate-800 text-slate-500 uppercase flex items-center gap-2">
          <Terminal size={14} /> Agent Reasoning
        </header>
        <div className="flex-1 overflow-y-auto p-4 text-emerald-500/80 whitespace-pre-wrap">
          {logs.length === 0 && <span className="opacity-50">Listening for agent events...</span>}
          {logs.join("")}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* ----------------- Pane 3: Live UI Preview (50%) ----------------- */}
      <div className="flex-1 flex flex-col bg-white">
        <header className="p-2 border-b border-slate-200 bg-slate-50 text-slate-600 flex justify-between items-center text-sm shadow-sm z-10">
           <span className="flex items-center gap-2 font-medium"><Code2 size={16} className="text-blue-500"/> Live Preview Workspace</span>
           <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full font-medium flex items-center gap-1">
             <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> HMR Active
           </span>
        </header>
        <iframe 
          key={iframeKey}
          src="http://localhost:5173?mode=app" 
          className="flex-1 w-full border-none"
          title="Generated UI"
        />
      </div>

    </div>
  )
}
