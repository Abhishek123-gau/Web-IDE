import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'

export default function Register() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      await api.post('/auth/register', { email, password })
      navigate('/login')
    } catch (err) {
      alert("Registration failed")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
      <div className="bg-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent mb-6 text-center">Join Nexus</h2>
        <form onSubmit={handleRegister} className="flex flex-col gap-4">
          <input 
            type="email" 
            placeholder="Email address" 
            className="p-3 rounded bg-slate-700 border border-slate-600 focus:outline-none focus:border-emerald-500"
            value={email} onChange={e => setEmail(e.target.value)} required 
          />
          <input 
            type="password" 
            placeholder="Password" 
            className="p-3 rounded bg-slate-700 border border-slate-600 focus:outline-none focus:border-emerald-500"
            value={password} onChange={e => setPassword(e.target.value)} required 
          />
          <button className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded transition-colors shadow-[0_0_15px_rgba(5,150,105,0.4)]">
            Create Account
          </button>
        </form>
        <p className="mt-4 text-center text-slate-400">
          Already have an account? <Link to="/login" className="text-emerald-400 hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  )
}
