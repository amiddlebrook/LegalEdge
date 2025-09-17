import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { MainLayout } from './layouts/MainLayout.jsx'
import { DashboardPage } from './pages/Dashboard.jsx'
import { OverviewPage } from './pages/Overview.jsx'
import { CoveragePage } from './pages/Coverage.jsx'
import { NotFoundPage } from './pages/NotFound.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="coverage" element={<CoveragePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}