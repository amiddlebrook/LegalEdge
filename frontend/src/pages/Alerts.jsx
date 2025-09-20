import { AlertManagement } from '../components/AlertManagement'

export function AlertsPage() {
  // Mock data for demonstration
  const mockAlerts = [
    {
      id: '1',
      category: 'Legislation',
      title: 'House committee advances AI Accountability and Transparency Act',
      description: 'Committee markup scheduled for next week; compliance vendors projected to see increased demand.',
      severity: 'high',
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      relatedEntities: ['HR-1001', 'AIT']
    },
    {
      id: '2',
      category: 'Congressional Trades',
      title: 'Sen. Jane Doe discloses AIQ accumulation',
      description: 'Recent Form 4 filing indicates BUY activity aligned with procurement legislation.',
      severity: 'medium',
      createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      relatedEntities: ['S.4242', 'AIQ']
    },
    {
      id: '3',
      category: 'State Policy',
      title: 'California privacy task force proposes stricter AI audit language',
      description: 'Draft proposal includes quarterly audit requirements impacting data processors.',
      severity: 'medium',
      createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      relatedEntities: ['CA-Privacy-Board', 'CSPN']
    },
    {
      id: '4',
      category: 'Infrastructure',
      title: 'Senate schedules vote on critical infrastructure grants',
      description: 'Bipartisan support growing for $50B infrastructure resilience package.',
      severity: 'low',
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      relatedEntities: ['GRID', 'S.1001']
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

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <AlertManagement
        alerts={mockAlerts}
        onCreateSubscription={handleCreateSubscription}
        onUpdateSubscription={handleUpdateSubscription}
        onDeleteSubscription={handleDeleteSubscription}
      />
    </div>
  )
}
