import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Frontend from './pages/Frontend.jsx'

const renderRoot = () => {
  const urlParams = new URLSearchParams(window.location.search);
  
  // If the iframe wants the generated app, render App
  if (urlParams.get('mode') === 'app') {
    return <App />;
  }
  
  // Otherwise, default to the IDE Frontend
  return <Frontend />;
};

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {renderRoot()}
  </StrictMode>,
)
