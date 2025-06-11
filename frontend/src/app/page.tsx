import { AlertFeed } from '@/components/alerts/AlertFeed'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Black Swan Event Detection</h1>
          <p className="text-muted-foreground">
            Real-time cryptocurrency market anomaly detection powered by AI
          </p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AlertFeed />
          </div>
          
          <div className="space-y-6">
            <div className="rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">System Status</h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">AI Models</span>
                  <span className="text-green-500">Online</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Data Streams</span>
                  <span className="text-green-500">Active</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Analysis Queue</span>
                  <span>0 pending</span>
                </div>
              </div>
            </div>
            
            <div className="rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Events Today</span>
                  <span>0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Critical Alerts</span>
                  <span className="text-red-500">0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Accuracy</span>
                  <span>--</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}