'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useEventStore } from '@/stores/useEventStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { cn } from '@/lib/utils'

const severityConfig = {
  low: {
    icon: Info,
    color: 'text-green-500',
    bg: 'bg-green-500/10',
    border: 'border-green-500/20',
  },
  medium: {
    icon: AlertCircle,
    color: 'text-yellow-500',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
  },
  high: {
    icon: AlertTriangle,
    color: 'text-orange-500',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
  },
  critical: {
    icon: XCircle,
    color: 'text-red-500',
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    pulse: true,
  },
}

export function AlertFeed() {
  const { events, markAsRead, selectEvent } = useEventStore()
  const [isConnected, setIsConnected] = useState(false)

  useWebSocket({
    onConnect: () => setIsConnected(true),
    onDisconnect: () => setIsConnected(false),
  })

  // Filter for unread alerts only
  const unreadAlerts = events.filter(e => !e.isRead && e.severity !== 'low')

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Real-time Alerts</h2>
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'h-2 w-2 rounded-full',
              isConnected ? 'bg-green-500' : 'bg-red-500'
            )}
          />
          <span className="text-sm text-muted-foreground">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <AnimatePresence mode="popLayout">
        {unreadAlerts.map((alert) => {
          const config = severityConfig[alert.severity]
          const Icon = config.icon

          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: 100 }}
              transition={{ duration: 0.3 }}
              className={cn(
                'rounded-lg border p-4 cursor-pointer transition-all hover:shadow-lg',
                config.bg,
                config.border,
                'pulse' in config && config.pulse && 'animate-pulse-ring'
              )}
              onClick={() => {
                markAsRead(alert.id)
                selectEvent(alert.id)
              }}
            >
              <div className="flex items-start gap-3">
                <Icon className={cn('h-5 w-5 mt-0.5', config.color)} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-medium">{alert.title}</h3>
                    <span className="text-xs text-muted-foreground">
                      {formatDistanceToNow(alert.timestamp, { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {alert.description}
                  </p>
                  {alert.affectedAssets.length > 0 && (
                    <div className="flex gap-2 mt-2">
                      {alert.affectedAssets.map((asset) => (
                        <span
                          key={asset}
                          className="text-xs px-2 py-1 rounded-full bg-background"
                        >
                          {asset}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center gap-4 mt-3 text-xs">
                    <span className="text-muted-foreground">
                      Confidence: {Math.round(alert.confidence * 100)}%
                    </span>
                    <span className="text-muted-foreground">
                      Source: {alert.source}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>

      {unreadAlerts.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>No active alerts</p>
        </div>
      )}
    </div>
  )
}