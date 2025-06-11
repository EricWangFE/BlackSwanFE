import { useEffect, useRef } from 'react'
import { socketManager } from '@/lib/websocket/socket'

interface UseWebSocketOptions {
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
  autoConnect?: boolean
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onConnect, onDisconnect, onError, autoConnect = true } = options
  const cleanupRef = useRef<(() => void)[]>([])

  useEffect(() => {
    if (autoConnect) {
      socketManager.connect()
    }

    // Set up event handlers
    if (onConnect) {
      socketManager.on('connect', onConnect)
      cleanupRef.current.push(() => socketManager.off('connect', onConnect))
    }

    if (onDisconnect) {
      socketManager.on('disconnect', onDisconnect)
      cleanupRef.current.push(() => socketManager.off('disconnect', onDisconnect))
    }

    if (onError) {
      socketManager.on('connect_error', onError)
      cleanupRef.current.push(() => socketManager.off('connect_error', onError))
    }

    // Cleanup
    return () => {
      cleanupRef.current.forEach(cleanup => cleanup())
      cleanupRef.current = []
      
      if (autoConnect) {
        socketManager.disconnect()
      }
    }
  }, [autoConnect, onConnect, onDisconnect, onError])

  return {
    socket: socketManager,
    isConnected: socketManager.isConnected,
    connect: () => socketManager.connect(),
    disconnect: () => socketManager.disconnect(),
    emit: (event: string, data: any) => socketManager.emit(event, data),
    on: (event: string, handler: (...args: any[]) => void) => {
      socketManager.on(event, handler)
      cleanupRef.current.push(() => socketManager.off(event, handler))
    },
    off: (event: string, handler?: (...args: any[]) => void) => 
      socketManager.off(event, handler)
  }
}