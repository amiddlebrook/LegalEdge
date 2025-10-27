import { useState } from 'react'
import { BarChart3, PieChart, TrendingUp, Users, Settings, Bell, Shield, FileText } from 'lucide-react'
import { Button } from './ui/index.jsx'
import { Badge } from './ui/index.jsx'

const personaConfigs = {
  investor: {
    name: 'Portfolio Manager',
    description: 'Focus on investment opportunities and risk management',
    icon: <TrendingUp className="w-5 h-5" />,
    primaryColor: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/20',
    features: [
      'Market opportunity analysis',
      'Portfolio conflict detection',
      'Risk-adjusted returns',
      'Investment timeline tracking'
    ],
    dashboard: {
      widgets: ['portfolio-metrics', 'opportunity-radar', 'conflict-alerts', 'sector-exposure'],
      charts: ['returns-timeline', 'risk-distribution', 'sector-allocation']
    }
  },
  analyst: {
    name: 'Policy Analyst',
    description: 'Deep dive into legislative intelligence and market impact',
    icon: <BarChart3 className="w-5 h-5" />,
    primaryColor: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    features: [
      'Legislative trend analysis',
      'Policy impact modeling',
      'Sector-specific insights',
      'Regulatory change tracking'
    ],
    dashboard: {
      widgets: ['legislation-tracker', 'policy-heatmap', 'analyst-notes', 'coverage-metrics'],
      charts: ['sentiment-trends', 'enactment-probability', 'jurisdiction-coverage']
    }
  },
  admin: {
    name: 'System Administrator',
    description: 'Manage platform, users, and system health',
    icon: <Settings className="w-5 h-5" />,
    primaryColor: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/20',
    features: [
      'User management',
      'System monitoring',
      'Data quality oversight',
      'Platform configuration'
    ],
    dashboard: {
      widgets: ['system-health', 'user-analytics', 'data-quality', 'audit-logs'],
      charts: ['user-growth', 'system-performance', 'data-completeness']
    }
  }
}

export function PersonaWorkflowSelector({ currentPersona, onPersonaChange, userRole }) {
  const [selectedPersona, setSelectedPersona] = useState(currentPersona || 'investor')

  const handlePersonaChange = (persona) => {
    setSelectedPersona(persona)
    onPersonaChange?.(persona)
  }

  const config = personaConfigs[selectedPersona]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-white mb-2">Choose Your Workflow</h2>
        <p className="text-sm text-slate-400">
          Select the interface that best matches your role and objectives
        </p>
      </div>

      {/* Persona Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(personaConfigs).map(([key, persona]) => (
          <PersonaCard
            key={key}
            persona={key}
            config={persona}
            isSelected={selectedPersona === key}
            onClick={() => handlePersonaChange(key)}
          />
        ))}
      </div>

      {/* Selected Persona Details */}
      <div className={`rounded-xl border p-6 ${config.borderColor} ${config.bgColor}`}>
        <div className="flex items-start gap-4">
          <div className={`${config.primaryColor} opacity-20 p-3 rounded-xl`}>
            {config.icon}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-xl font-semibold text-white">{config.name}</h3>
              <Badge className="bg-slate-700 text-slate-300">
                Active Workflow
              </Badge>
            </div>
            <p className="text-slate-300 mb-4">{config.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-slate-400 mb-2">Key Features</h4>
                <ul className="space-y-1">
                  {config.features.map((feature, index) => (
                    <li key={index} className="text-sm text-slate-300 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-current rounded-full opacity-60" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-400 mb-2">Dashboard Widgets</h4>
                <div className="space-y-2">
                  {config.dashboard.widgets.map((widget, index) => (
                    <div key={index} className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded">
                      {widget.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Customization */}
      <WorkflowCustomizer
        persona={selectedPersona}
        config={config}
        userRole={userRole}
      />
    </div>
  )
}

function PersonaCard({ persona, config, isSelected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-xl border text-left transition-all duration-200 ${
        isSelected
          ? `${config.borderColor} ${config.bgColor} border-2`
          : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`${config.primaryColor} opacity-20 p-2 rounded-lg`}>
          {config.icon}
        </div>
        <div className="flex-1">
          <h3 className="font-medium text-white mb-1">{config.name}</h3>
          <p className="text-sm text-slate-400">{config.description}</p>
          {isSelected && (
            <Badge className="mt-2 bg-slate-700 text-slate-300">
              Selected
            </Badge>
          )}
        </div>
      </div>
    </button>
  )
}

function WorkflowCustomizer({ persona, config, userRole }) {
  const [customizations, setCustomizations] = useState({
    notifications: true,
    autoRefresh: true,
    compactView: false,
    advancedFilters: userRole === 'admin' || userRole === 'analyst'
  })

  const toggleCustomization = (key) => {
    setCustomizations(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Customize Your Experience</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-slate-400">Display Options</h4>
          <label className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Enable notifications</span>
            <button
              onClick={() => toggleCustomization('notifications')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                customizations.notifications ? 'bg-primary' : 'bg-slate-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  customizations.notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </label>

          <label className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Auto-refresh data</span>
            <button
              onClick={() => toggleCustomization('autoRefresh')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                customizations.autoRefresh ? 'bg-primary' : 'bg-slate-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  customizations.autoRefresh ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </label>

          <label className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Compact view</span>
            <button
              onClick={() => toggleCustomization('compactView')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                customizations.compactView ? 'bg-primary' : 'bg-slate-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  customizations.compactView ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </label>
        </div>

        <div className="space-y-3">
          <h4 className="text-sm font-medium text-slate-400">Advanced Features</h4>
          {customizations.advancedFilters && (
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Shield className="w-4 h-4" />
              Advanced filters enabled
            </div>
          )}
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <FileText className="w-4 h-4" />
            Export capabilities available
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <Bell className="w-4 h-4" />
            Real-time alerts active
          </div>
        </div>
      </div>

      <div className="flex justify-end mt-6">
        <Button className="flex items-center gap-2">
          Apply Changes
        </Button>
      </div>
    </div>
  )
}
