import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { ApiCacheProvider } from './context/ApiCacheContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ApiCacheProvider>
      <App />
    </ApiCacheProvider>
  </StrictMode>,
)