import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { ApiCacheProvider } from './context/ApiCacheContext.jsx'
import { QueryProvider } from './context/QueryProvider.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryProvider>
      <ApiCacheProvider>
        <App />
      </ApiCacheProvider>
    </QueryProvider>
  </StrictMode>,
)
