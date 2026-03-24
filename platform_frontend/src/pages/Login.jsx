import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('token', data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError("Invalid credentials")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
      <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-6 text-center">Nexus Platform</h2>
        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <input 
            type="email" 
            placeholder="Email address" 
            className="p-3 rounded bg-slate-700 border border-slate-600 focus:outline-none focus:border-blue-500"
            value={email} onChange={e => setEmail(e.target.value)} required 
          />
          <input 
            type="password" 
            placeholder="Password" 
            className="p-3 rounded bg-slate-700 border border-slate-600 focus:outline-none focus:border-blue-500"
            value={password} onChange={e => setPassword(e.target.value)} required 
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">
            Sign In
          </button>
        </form>
        <p className="mt-4 text-center text-slate-400">
          Don't have an account? <Link to="/register" className="text-blue-400 hover:underline">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
