import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { FolderPlus, FolderOpen, LogOut, Clock } from 'lucide-react'
import api from '../api'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const { data } = await api.get('/projects/')
      setProjects(data)
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token')
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async () => {
    const title = prompt("Enter a name for your new AI Project:")
    if (!title) return
    
    try {
      const { data } = await api.post('/projects/', { title })
      navigate(`/project/${data.id}`)
    } catch (err) {
      alert("Failed to create project")
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-12 border-b border-slate-800 pb-6">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Nexus Dashboard
          </h1>
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <LogOut size={18} /> Logout
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Create New Card */}
          <div 
            onClick={handleCreateProject}
            className="group cursor-pointer border-2 border-dashed border-slate-700 hover:border-blue-500 rounded-2xl p-8 flex flex-col items-center justify-center text-slate-400 hover:text-blue-400 hover:bg-slate-800/50 transition-all shadow-none hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] min-h-[200px]"
          >
            <FolderPlus size={48} className="mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-xl font-bold">New Project</h3>
            <p className="text-sm text-center mt-2 opacity-70">Initialize a blank AI UI workspace instantly.</p>
          </div>

          {/* Project List */}
          {loading ? (
            <p className="col-span-full text-slate-500 text-center py-12 animate-pulse">Loading workspace data...</p>
          ) : (
            projects.map(p => (
              <div 
                key={p.id} 
                onClick={() => navigate(`/project/${p.id}`)}
                className="cursor-pointer bg-slate-800 border border-slate-700 hover:border-slate-500 rounded-2xl p-6 flex flex-col justify-between transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-black/50 min-h-[200px]"
              >
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
                      <FolderOpen size={24} />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-slate-100 truncate">{p.title}</h3>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-slate-500 mt-4 border-t border-slate-700 pt-4">
                  <Clock size={14} /> 
                  Last edited {new Date(p.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
