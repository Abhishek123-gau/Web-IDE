import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ProjectIDE from './pages/ProjectIDE'

function App() {
  const isAuthenticated = !!localStorage.getItem("token")

  return (
    <Routes>
      <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/project/:id" element={<ProjectIDE />} />
    </Routes>
  )
}

export default App
