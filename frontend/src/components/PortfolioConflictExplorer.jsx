import { useState, useMemo } from 'react'
import { Search, Filter, AlertTriangle, TrendingUp, TrendingDown, Eye, EyeOff } from 'lucide-react'
import { Button } from './ui/index.jsx'
import { Input } from './ui/index.jsx'
import { Select } from './ui/index.jsx'
import { Badge } from './ui/index.jsx'

const conflictColors = {
  high: 'bg-red-500/10 text-red-400 border-red-500/20',
  medium: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  low: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
}

const jurisdictionColors = {
  Federal: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  'New York': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  California: 'bg-green-500/10 text-green-400 border-green-500/20',
  Texas: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
}

export function PortfolioConflictExplorer({ conflicts = [], onResolveConflict, onExportConflicts }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [riskFilter, setRiskFilter] = useState('all')
  const [jurisdictionFilter, setJurisdictionFilter] = useState('all')
  const [sortBy, setSortBy] = useState('risk')
  const [sortOrder, setSortOrder] = useState('desc')
  const [hiddenTickers, setHiddenTickers] = useState(new Set())

  const filteredConflicts = useMemo(() => {
    let filtered = conflicts.filter(conflict => {
      const matchesSearch = conflict.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          conflict.member.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          conflict.billTitle.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesRisk = riskFilter === 'all' || conflict.riskScore >= getRiskThreshold(riskFilter)
      const matchesJurisdiction = jurisdictionFilter === 'all' || conflict.jurisdiction === jurisdictionFilter

      return matchesSearch && matchesRisk && matchesJurisdiction && !hiddenTickers.has(conflict.ticker)
    })

    // Sort conflicts
    filtered.sort((a, b) => {
      let aValue, bValue

      switch (sortBy) {
        case 'risk':
          aValue = a.riskScore
          bValue = b.riskScore
          break
        case 'ticker':
          aValue = a.ticker
          bValue = b.ticker
          break
        case 'member':
          aValue = a.member
          bValue = b.member
          break
        case 'date':
          aValue = new Date(a.transactionDate)
          bValue = new Date(b.transactionDate)
          break
        default:
          aValue = a.riskScore
          bValue = b.riskScore
      }

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [conflicts, searchTerm, riskFilter, jurisdictionFilter, sortBy, sortOrder, hiddenTickers])

  const conflictStats = useMemo(() => {
    const total = conflicts.length
    const highRisk = conflicts.filter(c => c.riskScore >= 70).length
    const mediumRisk = conflicts.filter(c => c.riskScore >= 40 && c.riskScore < 70).length
    const lowRisk = conflicts.filter(c => c.riskScore < 40).length

    const byJurisdiction = conflicts.reduce((acc, conflict) => {
      acc[conflict.jurisdiction] = (acc[conflict.jurisdiction] || 0) + 1
      return acc
    }, {})

    const topTickers = conflicts
      .reduce((acc, conflict) => {
        acc[conflict.ticker] = (acc[conflict.ticker] || 0) + 1
        return acc
      }, {})
    const topConflictedTickers = Object.entries(topTickers)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([ticker, count]) => ({ ticker, count }))

    return {
      total,
      highRisk,
      mediumRisk,
      lowRisk,
      byJurisdiction,
      topConflictedTickers
    }
  }, [conflicts])

  const toggleTickerVisibility = (ticker) => {
    const newHidden = new Set(hiddenTickers)
    if (newHidden.has(ticker)) {
      newHidden.delete(ticker)
    } else {
      newHidden.add(ticker)
    }
    setHiddenTickers(newHidden)
  }

  const getRiskLevel = (riskScore) => {
    if (riskScore >= 70) return 'high'
    if (riskScore >= 40) return 'medium'
    return 'low'
  }

  const getRiskThreshold = (level) => {
    switch (level) {
      case 'high': return 70
      case 'medium': return 40
      case 'low': return 0
      default: return 0
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">Portfolio Conflict Explorer</h2>
          <p className="text-sm text-slate-400 mt-1">
            Analyze potential conflicts between congressional trades and pending legislation
          </p>
        </div>
        <Button onClick={onExportConflicts} className="flex items-center gap-2">
          Export Conflicts
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Conflicts"
          value={conflictStats.total}
          icon={<AlertTriangle className="w-5 h-5" />}
        />
        <StatCard
          title="High Risk"
          value={conflictStats.highRisk}
          icon={<TrendingUp className="w-5 h-5" />}
          color="text-red-400"
        />
        <StatCard
          title="Medium Risk"
          value={conflictStats.mediumRisk}
          icon={<TrendingDown className="w-5 h-5" />}
          color="text-yellow-400"
        />
        <StatCard
          title="Low Risk"
          value={conflictStats.lowRisk}
          icon={<TrendingDown className="w-5 h-5" />}
          color="text-green-400"
        />
      </div>

      {/* Top Conflicted Tickers */}
      <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Most Conflicted Tickers</h3>
        <div className="space-y-2">
          {conflictStats.topConflictedTickers.map(({ ticker, count }) => (
            <div key={ticker} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-slate-300 font-medium">{ticker}</span>
                <span className="text-sm text-slate-500">{count} conflicts</span>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => toggleTickerVisibility(ticker)}
                className="text-slate-400 hover:text-white"
              >
                {hiddenTickers.has(ticker) ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <Input
              placeholder="Search conflicts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select
          value={riskFilter}
          onChange={setRiskFilter}
          className="w-full sm:w-48"
        >
          <option value="all">All Risk Levels</option>
          <option value="high">High Risk (70+)</option>
          <option value="medium">Medium Risk (40-69)</option>
          <option value="low">Low Risk (&lt;40)</option>
        </Select>
        <Select
          value={jurisdictionFilter}
          onChange={setJurisdictionFilter}
          className="w-full sm:w-48"
        >
          <option value="all">All Jurisdictions</option>
          <option value="Federal">Federal</option>
          <option value="New York">New York</option>
          <option value="California">California</option>
          <option value="Texas">Texas</option>
        </Select>
        <Select
          value={`${sortBy}-${sortOrder}`}
          onChange={(e) => {
            const [field, order] = e.target.value.split('-')
            setSortBy(field)
            setSortOrder(order)
          }}
          className="w-full sm:w-48"
        >
          <option value="risk-desc">Risk Score (High to Low)</option>
          <option value="risk-asc">Risk Score (Low to High)</option>
          <option value="ticker-asc">Ticker (A-Z)</option>
          <option value="ticker-desc">Ticker (Z-A)</option>
          <option value="member-asc">Member (A-Z)</option>
          <option value="member-desc">Member (Z-A)</option>
          <option value="date-desc">Date (Newest First)</option>
          <option value="date-asc">Date (Oldest First)</option>
        </Select>
      </div>

      {/* Conflicts List */}
      <div className="space-y-4">
        {filteredConflicts.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-300 mb-2">No conflicts found</h3>
            <p className="text-sm text-slate-400">
              {searchTerm || riskFilter !== 'all' || jurisdictionFilter !== 'all'
                ? 'Try adjusting your filters to see more conflicts.'
                : 'No conflicts match your current criteria.'}
            </p>
          </div>
        ) : (
          filteredConflicts.map((conflict) => (
            <ConflictCard
              key={`${conflict.ticker}-${conflict.member}`}
              conflict={conflict}
              onResolve={onResolveConflict}
            />
          ))
        )}
      </div>
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

function ConflictCard({ conflict, onResolve }) {
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getRiskLevel = (riskScore) => {
    if (riskScore >= 70) return 'high'
    if (riskScore >= 40) return 'medium'
    return 'low'
  }

  const riskLevel = getRiskLevel(conflict.riskScore)

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">{conflict.ticker}</h3>
          <Badge className={conflictColors[riskLevel]}>
            Risk: {conflict.riskScore}
          </Badge>
          <Badge className={jurisdictionColors[conflict.jurisdiction]}>
            {conflict.jurisdiction}
          </Badge>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onResolve(conflict)}
          className="text-slate-400 hover:text-white"
        >
          Resolve
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-slate-400 mb-1">Congressional Member</p>
          <p className="text-slate-300">{conflict.member} ({conflict.chamber})</p>
        </div>
        <div>
          <p className="text-sm text-slate-400 mb-1">Transaction</p>
          <p className="text-slate-300">
            {conflict.transactionType} on {formatDate(conflict.transactionDate)}
          </p>
        </div>
        <div className="md:col-span-2">
          <p className="text-sm text-slate-400 mb-1">Related Legislation</p>
          <p className="text-slate-300">{conflict.billTitle}</p>
          <p className="text-sm text-slate-500 mt-1">Stage: {conflict.billStage}</p>
        </div>
      </div>

      {conflict.rationale && (
        <div>
          <p className="text-sm text-slate-400 mb-1">Analysis</p>
          <p className="text-sm text-slate-300">{conflict.rationale}</p>
        </div>
      )}
    </div>
  )
}
