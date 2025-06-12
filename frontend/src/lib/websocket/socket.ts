import { io, Socket } from 'socket.io-client'
import { useEventStore } from '@/stores/useEventStore'

class SocketManager {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(): void {
    if (this.socket?.connected) return

    const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL || 
      (process.env.REPL_SLUG ? `wss://${process.env.REPL_SLUG}.${process.env.REPL_OWNER}.repl.co:8000` : 'http://localhost:8000')
    
    this.socket = io(socketUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      reconnectionDelayMax: 10000,
      timeout: 20000,
      autoConnect: true,
      auth: {
        token: this.getAuthToken()
      }
    })

    this.setupEventHandlers()
  }

  private setupEventHandlers(): void {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      useEventStore.getState().setError(null)
      
      // Subscribe to event channels
      this.socket?.emit('subscribe', {
        channels: ['events:analyzed', 'alerts:critical']
      })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, attempt to reconnect
        this.socket?.connect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        useEventStore.getState().setError('Unable to connect to real-time updates')
      }
    })

    // Handle incoming events
    this.socket.on('event:new', (data) => {
      const event = {
        ...data,
        timestamp: new Date(data.timestamp),
        isRead: false
      }
      useEventStore.getState().addEvent(event)
    })

    this.socket.on('event:update', (data) => {
      const { events } = useEventStore.getState()
      const updatedEvents = events.map(e => 
        e.id === data.id ? { ...e, ...data } : e
      )
      useEventStore.setState({ events: updatedEvents })
    })

    this.socket.on('alert:critical', (alert) => {
      // Handle critical alerts with special UI treatment
      console.warn('Critical alert received:', alert)
      // Could trigger notifications, sounds, etc.
    })

    // Heartbeat to keep connection alive
    this.socket.on('ping', () => {
      this.socket?.emit('pong')
    })
  }

  private getAuthToken(): string {
    // Get auth token from NextAuth session or cookies
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth-token') || ''
    }
    return ''
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  emit(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('Socket not connected, queuing event:', event)
    }
  }

  on(event: string, handler: (...args: any[]) => void): void {
    this.socket?.on(event, handler)
  }

  off(event: string, handler?: (...args: any[]) => void): void {
    this.socket?.off(event, handler)
  }

  get isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

// Export singleton instance
export const socketManager = new SocketManager()