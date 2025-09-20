import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs'
import { AlertManagement } from '../components/AlertManagement'
import { PortfolioConflictExplorer } from '../components/PortfolioConflictExplorer'
import { PersonaWorkflowSelector } from '../components/PersonaWorkflows'

export function SettingsPage({ user, onUpdateUser }) {
  const [activeTab, setActiveTab] = useState('alerts')

  // Mock data for demonstration
  const mockConflicts = [
    {
      ticker: 'AIT',
      member: 'Sen. Jane Doe',
      chamber: 'Senate',
      transactionType: 'BUY',
      transactionDate: '2024-01-15',
      amountRange: '$15,001 - $50,000',
      billTitle: 'AI Accountability and Transparency Act',
      billStage: 'Committee',
      jurisdiction: 'Federal',
      nextActionDate: '2024-02-15',
      riskScore: 85,
      confidence: 0.92,
      rationale: 'Direct overlap between AIQ holdings and pending AI regulation legislation. High risk of material impact on stock price.'
    },
    {
      ticker: 'REGN',
      member: 'Rep. Alex Smith',
      chamber: 'House',
      transactionType: 'SELL',
      transactionDate: '2024-01-10',
      amountRange: '$50,001 - $100,000',
      billTitle: 'California Algorithmic Accountability Framework',
      billStage: 'Assembly',
      jurisdiction: 'California',
      nextActionDate: '2024-02-01',
      riskScore: 72,
      confidence: 0.78,
      rationale: 'State-level regulation could impact regtech sector compliance costs and market dynamics.'
    },
    {
      ticker: 'GRID',
      member: 'Sen. Malik Johnson',
      chamber: 'Senate',
      transactionType: 'BUY',
      transactionDate: '2024-01-08',
      amountRange: '$100,001 - $250,000',
      billTitle: 'Texas Critical Infrastructure Cyber Resilience Act',
      billStage: 'Senate',
      jurisdiction: 'Texas',
      nextActionDate: '2024-01-25',
      riskScore: 45,
      confidence: 0.65,
      rationale: 'Infrastructure spending bill likely to benefit utilities sector but impact on individual companies uncertain.'
    }
  ]

  const handleCreateSubscription = (subscription) => {
    console.log('Creating subscription:', subscription)
    // TODO: Implement API call
  }

  const handleUpdateSubscription = (id, updates) => {
    console.log('Updating subscription:', id, updates)
    // TODO: Implement API call
  }

  const handleDeleteSubscription = (id) => {
    console.log('Deleting subscription:', id)
    // TODO: Implement API call
  }

  const handleResolveConflict = (conflict) => {
    console.log('Resolving conflict:', conflict)
    // TODO: Implement API call
  }

  const handleExportConflicts = () => {
    console.log('Exporting conflicts')
    // TODO: Implement export functionality
  }

  const handlePersonaChange = (persona) => {
    console.log('Changing persona to:', persona)
    // TODO: Implement persona change
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-white mb-2">Settings & Workflows</h1>
        <p className="text-slate-400">
          Customize your LegalEdge experience and manage your preferences
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 bg-slate-800/50 border border-slate-700">
          <TabsTrigger
            value="alerts"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
          >
            Alert Management
          </TabsTrigger>
          <TabsTrigger
            value="conflicts"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
          >
            Conflict Explorer
          </TabsTrigger>
          <TabsTrigger
            value="workflows"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
          >
            Workflows
          </TabsTrigger>
          <TabsTrigger
            value="preferences"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
          >
            Preferences
          </TabsTrigger>
        </TabsList>

        <TabsContent value="alerts" className="space-y-6">
          <AlertManagement
            alerts={[]} // TODO: Fetch from API
            onCreateSubscription={handleCreateSubscription}
            onUpdateSubscription={handleUpdateSubscription}
            onDeleteSubscription={handleDeleteSubscription}
          />
        </TabsContent>

        <TabsContent value="conflicts" className="space-y-6">
          <PortfolioConflictExplorer
            conflicts={mockConflicts}
            onResolveConflict={handleResolveConflict}
            onExportConflicts={handleExportConflicts}
          />
        </TabsContent>

        <TabsContent value="workflows" className="space-y-6">
          <PersonaWorkflowSelector
            currentPersona={user?.preferences?.persona || 'investor'}
            onPersonaChange={handlePersonaChange}
            userRole={user?.role || 'investor'}
          />
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <UserPreferences
            user={user}
            onUpdate={onUpdateUser}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function UserPreferences({ user, onUpdate }) {
  const [preferences, setPreferences] = useState(user?.preferences || {
    theme: 'dark',
    notifications: 'important',
    refreshInterval: 30,
    exportFormat: 'csv',
    timezone: 'UTC',
    language: 'en'
  })

  const handleSave = () => {
    onUpdate?.({ preferences })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white mb-2">User Preferences</h2>
        <p className="text-sm text-slate-400">
          Customize your LegalEdge experience
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Display Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Theme
              </label>
              <select
                value={preferences.theme}
                onChange={(e) => setPreferences({...preferences, theme: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="auto">Auto</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Language
              </label>
              <select
                value={preferences.language}
                onChange={(e) => setPreferences({...preferences, language: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Timezone
              </label>
              <select
                value={preferences.timezone}
                onChange={(e) => setPreferences({...preferences, timezone: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Notification Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Notification Level
              </label>
              <select
                value={preferences.notifications}
                onChange={(e) => setPreferences({...preferences, notifications: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value="all">All notifications</option>
                <option value="important">Important only</option>
                <option value="critical">Critical only</option>
                <option value="none">No notifications</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Data Refresh Interval (seconds)
              </label>
              <select
                value={preferences.refreshInterval}
                onChange={(e) => setPreferences({...preferences, refreshInterval: parseInt(e.target.value)})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value={15}>15 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Default Export Format
              </label>
              <select
                value={preferences.exportFormat}
                onChange={(e) => setPreferences({...preferences, exportFormat: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-100"
              >
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
                <option value="excel">Excel</option>
                <option value="pdf">PDF</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Save Preferences
        </button>
      </div>
    </div>
  )
}
