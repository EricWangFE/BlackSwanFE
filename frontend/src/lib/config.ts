// Dynamic configuration for Replit deployment

const isReplit = process.env.REPL_SLUG !== undefined

// In Replit, construct URLs from environment
const replitUrl = isReplit 
  ? `https://${process.env.REPL_SLUG}.${process.env.REPL_OWNER}.repl.co`
  : ''

export const config = {
  api: {
    url: process.env.NEXT_PUBLIC_API_URL || (isReplit ? `${replitUrl}:8000` : 'http://localhost:8000'),
    socketUrl: process.env.NEXT_PUBLIC_SOCKET_URL || (isReplit ? `wss://${process.env.REPL_SLUG}.${process.env.REPL_OWNER}.repl.co:8000` : 'ws://localhost:8000')
  },
  auth: {
    url: process.env.NEXTAUTH_URL || (isReplit ? replitUrl : 'http://localhost:3000')
  }
}