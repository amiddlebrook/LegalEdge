import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Area,
  AreaChart,
} from 'recharts'
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign, Activity, Users } from 'lucide-react'

const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#6366f1']

export function DashboardCharts({ dashboard, filters }) {
  const chartData = useMemo(() => {
    // Generate time series data for trends
    const now = new Date()
    const timeSeries = Array.from({ length: 30 }, (_, i) => {
      const date = new Date(now)
      date.setDate(date.getDate() - (29 - i))
      return {
        date: date.toISOString().split('T')[0],
        alerts: Math.floor(Math.random() * 5) + (i % 7 === 0 ? 8 : 0),
        opportunities: Math.floor(Math.random() * 3) + 1,
        legislationActivity: Math.floor(Math.random() * 10) + 5,
        marketSentiment: Math.random() * 40 + 50,
      }
    })

    // Sector distribution data
    const sectorData = [
      { name: 'Technology', value: 35, count: 12 },
      { name: 'Financial Services', value: 25, count: 8 },
      { name: 'Healthcare', value: 20, count: 6 },
      { name: 'Energy', value: 12, count: 4 },
      { name: 'Industrials', value: 8, count: 3 },
    ]

    // Risk distribution
    const riskData = [
      { name: 'Low', value: 45, count: 15 },
      { name: 'Balanced', value: 30, count: 10 },
      { name: 'Medium', value: 20, count: 7 },
      { name: 'High', value: 5, count: 2 },
    ]

    // Alert severity trends
    const alertTrends = [
      { month: 'Jan', critical: 2, high: 8, medium: 15, low: 25 },
      { month: 'Feb', critical: 1, high: 6, medium: 12, low: 22 },
      { month: 'Mar', critical: 3, high: 10, medium: 18, low: 28 },
      { month: 'Apr', critical: 1, high: 7, medium: 14, low: 20 },
    ]

    return { timeSeries, sectorData, riskData, alertTrends }
  }, [filters])

  const metrics = useMemo(() => {
    const alertCount = dashboard.alerts.length
    const opportunityCount = dashboard.opportunities.length
    const legislationCount = dashboard.upcomingLegislation.length
    const avgConfidence = dashboard.opportunities.reduce((acc, opp) => acc + opp.conviction, 0) / opportunityCount || 0
    const highRiskAlerts = dashboard.alerts.filter(alert => alert.severity === 'high' || alert.severity === 'critical').length

    return {
      alertCount,
      opportunityCount,
      legislationCount,
      avgConfidence: Math.round(avgConfidence * 100),
      highRiskAlerts,
    }
  }, [dashboard])

  return (
    <div className="space-y-8">
      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Alerts"
          value={metrics.alertCount}
          icon={<AlertTriangle className="w-5 h-5" />}
          trend={metrics.alertCount > 10 ? 'up' : 'down'}
          color="text-orange-400"
          bgColor="bg-orange-500/10"
          borderColor="border-orange-500/20"
        />
        <MetricCard
          title="Opportunities"
          value={metrics.opportunityCount}
          icon={<DollarSign className="w-5 h-5" />}
          trend="up"
          color="text-green-400"
          bgColor="bg-green-500/10"
          borderColor="border-green-500/20"
        />
        <MetricCard
          title="Legislation Tracked"
          value={metrics.legislationCount}
          icon={<Activity className="w-5 h-5" />}
          trend="stable"
          color="text-blue-400"
          bgColor="bg-blue-500/10"
          borderColor="border-blue-500/20"
        />
        <MetricCard
          title="Avg Confidence"
          value={`${metrics.avgConfidence}%`}
          icon={<TrendingUp className="w-5 h-5" />}
          trend={metrics.avgConfidence > 70 ? 'up' : 'down'}
          color="text-purple-400"
          bgColor="bg-purple-500/10"
          borderColor="border-purple-500/20"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Activity Timeline */}
        <ChartCard title="30-Day Activity Trends" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.timeSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="date"
                stroke="#9ca3af"
                fontSize={12}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f9fafb'
                }}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="alerts"
                stackId="1"
                stroke="#f59e0b"
                fill="#f59e0b"
                fillOpacity={0.3}
                name="Alerts"
              />
              <Area
                type="monotone"
                dataKey="opportunities"
                stackId="1"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
                name="Opportunities"
              />
              <Area
                type="monotone"
                dataKey="legislationActivity"
                stackId="1"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.3}
                name="Legislation Activity"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Sector Distribution */}
        <ChartCard title="Sector Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.sectorData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.sectorData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f9fafb'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk Distribution */}
        <ChartCard title="Risk Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f9fafb'
                }}
              />
              <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Alert Trends */}
        <ChartCard title="Alert Severity Trends" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.alertTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f9fafb'
                }}
              />
              <Line
                type="monotone"
                dataKey="critical"
                stroke="#ef4444"
                strokeWidth={3}
                name="Critical"
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="high"
                stroke="#f59e0b"
                strokeWidth={2}
                name="High"
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="medium"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Medium"
                dot={{ r: 2 }}
              />
              <Line
                type="monotone"
                dataKey="low"
                stroke="#6b7280"
                strokeWidth={1}
                name="Low"
                dot={{ r: 1 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}

function MetricCard({ title, value, icon, trend, color, bgColor, borderColor }) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Activity

  return (
    <div className={`rounded-xl border p-6 ${borderColor} ${bgColor} transition-all duration-200 hover:scale-105`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
        </div>
        <div className={`${color} opacity-20`}>
          {icon}
        </div>
      </div>
      {trend !== 'stable' && (
        <div className="flex items-center mt-4">
          <TrendIcon className={`w-4 h-4 mr-1 ${color}`} />
          <span className="text-xs text-slate-400 capitalize">{trend} from last period</span>
        </div>
      )}
    </div>
  )
}

function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`rounded-xl border border-slate-800 bg-card-bg/60 p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      {children}
    </div>
  )
}
