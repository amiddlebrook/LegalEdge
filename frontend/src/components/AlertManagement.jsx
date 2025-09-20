import { useState, useMemo } from 'react'
import { Search, Filter, Plus, Bell, Settings, X, Check, AlertCircle } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import { Badge } from './ui/Badge'
import { Modal } from './ui/Modal'

const severityColors = {
  low: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  high: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  critical: 'bg-red-500/10 text-red-400 border-red-500/20',
}

const categoryColors = {
  Legislation: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  'Congressional Trades': 'bg-green-500/10 text-green-400 border-green-500/20',
  'State Policy': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  Infrastructure: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
}

export function AlertManagement({ alerts = [], onCreateSubscription, onUpdateSubscription, onDeleteSubscription }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState(null)

  const filteredAlerts = useMemo(() => {
    return alerts.filter(alert => {
      const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          alert.description.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter
      const matchesCategory = categoryFilter === 'all' || alert.category === categoryFilter

      return matchesSearch && matchesSeverity && matchesCategory
    })
  }, [alerts, searchTerm, severityFilter, categoryFilter])

  const alertStats = useMemo(() => {
    const total = alerts.length
    const bySeverity = alerts.reduce((acc, alert) => {
      acc[alert.severity] = (acc[alert.severity] || 0) + 1
      return acc
    }, {})
    const byCategory = alerts.reduce((acc, alert) => {
      acc[alert.category] = (acc[alert.category] || 0) + 1
      return acc
    }, {})

    return { total, bySeverity, byCategory }
  }, [alerts])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">Alert Management</h2>
          <p className="text-sm text-slate-400 mt-1">
            Monitor and manage policy alerts and notifications
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Subscription
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Total Alerts" value={alertStats.total} icon={<Bell className="w-5 h-5" />} />
        <StatCard title="Critical" value={alertStats.bySeverity.critical || 0} icon={<AlertCircle className="w-5 h-5" />} color="text-red-400" />
        <StatCard title="High" value={alertStats.bySeverity.high || 0} icon={<AlertCircle className="w-5 h-5" />} color="text-orange-400" />
        <StatCard title="Medium" value={alertStats.bySeverity.medium || 0} icon={<AlertCircle className="w-5 h-5" />} color="text-yellow-400" />
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              placeholder="Search alerts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select
          value={severityFilter}
          onChange={setSeverityFilter}
          className="w-full sm:w-48"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </Select>
        <Select
          value={categoryFilter}
          onChange={setCategoryFilter}
          className="w-full sm:w-48"
        >
          <option value="all">All Categories</option>
          <option value="Legislation">Legislation</option>
          <option value="Congressional Trades">Congressional Trades</option>
          <option value="State Policy">State Policy</option>
          <option value="Infrastructure">Infrastructure</option>
        </Select>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-300 mb-2">No alerts found</h3>
            <p className="text-sm text-slate-400">
              {searchTerm || severityFilter !== 'all' || categoryFilter !== 'all'
                ? 'Try adjusting your filters to see more alerts.'
                : 'No alerts match your current criteria.'}
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onClick={() => setSelectedAlert(alert)}
            />
          ))
        )}
      </div>

      {/* Create Subscription Modal */}
      {showCreateModal && (
        <CreateSubscriptionModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={onCreateSubscription}
        />
      )}

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
        />
      )}
    </div>
  )
}

function StatCard({ title, value, icon, color = 'text-slate-400' }) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
        </div>
        <div className={`${color} opacity-20`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function AlertCard({ alert, onClick }) {
  const formatTime = (date) => {
    const now = new Date()
    const alertDate = new Date(date)
    const diffMs = now - alertDate
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  return (
    <div
      onClick={onClick}
      className="bg-slate-800/50 rounded-xl border border-slate-700 p-4 hover:border-slate-600 transition-colors cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Badge className={severityColors[alert.severity]}>
              {alert.severity}
            </Badge>
            <Badge className={categoryColors[alert.category]}>
              {alert.category}
            </Badge>
            <span className="text-xs text-slate-500">
              {formatTime(alert.createdAt)}
            </span>
          </div>
          <h3 className="text-lg font-medium text-white mb-2">{alert.title}</h3>
          <p className="text-sm text-slate-300 line-clamp-2">{alert.description}</p>
          {alert.relatedEntities.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {alert.relatedEntities.slice(0, 3).map((entity) => (
                <span
                  key={entity}
                  className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded-full"
                >
                  {entity}
                </span>
              ))}
              {alert.relatedEntities.length > 3 && (
                <span className="text-xs text-slate-500">
                  +{alert.relatedEntities.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function CreateSubscriptionModal({ onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    label: '',
    categories: [],
    entities: [],
    severities: [],
    minSeverity: 'medium',
    channels: [{ type: 'email', target: '', isVerified: false }],
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
    onClose()
  }

  return (
    <Modal onClose={onClose}>
      <div className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Create Alert Subscription</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Subscription Name"
            value={formData.label}
            onChange={(e) => setFormData({...formData, label: e.target.value})}
            placeholder="e.g., High Priority Tech Legislation"
            required
          />

          <Select
            label="Minimum Severity"
            value={formData.minSeverity}
            onChange={(value) => setFormData({...formData, minSeverity: value})}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </Select>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              Create Subscription
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  )
}

function AlertDetailModal({ alert, onClose }) {
  return (
    <Modal onClose={onClose}>
      <div className="p-6 max-w-2xl">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Badge className={severityColors[alert.severity]}>
                {alert.severity}
              </Badge>
              <Badge className={categoryColors[alert.category]}>
                {alert.category}
              </Badge>
            </div>
            <h3 className="text-xl font-semibold text-white">{alert.title}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <p className="text-slate-300">{alert.description}</p>

          {alert.relatedEntities.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-400 mb-2">Related Entities</h4>
              <div className="flex flex-wrap gap-2">
                {alert.relatedEntities.map((entity) => (
                  <span
                    key={entity}
                    className="text-sm bg-slate-700 text-slate-300 px-2 py-1 rounded-full"
                  >
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span>Created: {new Date(alert.createdAt).toLocaleString()}</span>
            <span>ID: {alert.id}</span>
          </div>
        </div>
      </div>
    </Modal>
  )
}
