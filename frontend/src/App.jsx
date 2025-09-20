import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { QueryProvider } from './context/QueryProvider'
import { Toaster } from 'react-hot-toast'

import { MainLayout } from './layouts/MainLayout.jsx'
import { DashboardPage } from './pages/Dashboard.jsx'
import { OverviewPage } from './pages/Overview.jsx'
import { CoveragePage } from './pages/Coverage.jsx'
import { NotFoundPage } from './pages/NotFound.jsx'

export default function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-900">
          <Routes>
            <Route element={<MainLayout />}>
              <Route index element={<OverviewPage />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="coverage" element={<CoveragePage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1f2937',
                color: '#f9fafb',
                border: '1px solid #374151',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#1f2937',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#1f2937',
                },
              },
            }}
          />
        </div>
      </BrowserRouter>
    </QueryProvider>
  )
}