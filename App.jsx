import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import LoginForm from './components/LoginForm'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import apiService from './services/api'
import { Toaster } from '@/components/ui/sonner'
import { toast } from 'sonner'
import './App.css'

function AppContent() {
  const { user, isLoading: authLoading, error: authError, login, logout, isAuthenticated } = useAuth()
  
  // Chat state
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)
  const [activeTool, setActiveTool] = useState('chat')

  // Load chat sessions when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadChatSessions()
    }
  }, [isAuthenticated])

  // Load messages when session changes
  useEffect(() => {
    if (currentSession) {
      loadChatMessages(currentSession.id)
    } else {
      setMessages([])
    }
  }, [currentSession])

  const loadChatSessions = async () => {
    try {
      const sessionsData = await apiService.getChatSessions()
      setSessions(sessionsData)
      
      // Auto-select the most recent session if none selected
      if (!currentSession && sessionsData.length > 0) {
        setCurrentSession(sessionsData[0])
      }
    } catch (error) {
      console.error('Failed to load chat sessions:', error)
      toast.error("Failed to load chat sessions")
    }
  }

  const loadChatMessages = async (sessionId) => {
    try {
      setIsLoadingMessages(true)
      const messagesData = await apiService.getChatMessages(sessionId)
      setMessages(messagesData)
    } catch (error) {
      console.error('Failed to load messages:', error)
      toast.error("Failed to load chat messages")
    } finally {
      setIsLoadingMessages(false)
    }
  }

  const handleNewSession = async () => {
    try {
      const sessionName = `Chat ${new Date().toLocaleString()}`
      const newSession = await apiService.createChatSession(sessionName)
      
      setSessions(prev => [newSession, ...prev])
      setCurrentSession(newSession)
      
      toast.success("New chat session created")
    } catch (error) {
      console.error('Failed to create session:', error)
      toast.error("Failed to create new chat session")
    }
  }

  const handleSessionSelect = (session) => {
    setCurrentSession(session)
  }

  const handleSendMessage = async (messageText, contextType = 'general') => {
    if (!currentSession) {
      // Create a new session if none exists
      await handleNewSession()
      return
    }

    try {
      setIsLoadingMessages(true)
      
      // Add user message to UI immediately
      const userMessage = {
        id: Date.now(),
        message_type: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      // Send message to backend
      const response = await apiService.sendMessage(currentSession.id, messageText, contextType)
      
      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        message_type: 'assistant',
        content: response.response || response.message?.content || 'No response received',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])

      // Refresh sessions to update last activity
      loadChatSessions()
      
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error("Failed to send message. Please try again.")
    } finally {
      setIsLoadingMessages(false)
    }
  }

  const handleToolSelect = (toolId) => {
    setActiveTool(toolId)
    
    // For now, all tools use the chat interface
    // In a full implementation, different tools might have different UIs
    if (toolId !== 'chat') {
      toast.info(`Switched to ${toolId} mode. Use the chat to interact with this tool.`)
    }
  }

  const handleLogin = async (credentials) => {
    const result = await login(credentials)
    if (result.success) {
      toast.success(`Welcome ${credentials.username}!`)
    }
    return result
  }

  const handleLogout = async () => {
    await logout()
    setSessions([])
    setCurrentSession(null)
    setMessages([])
    toast.success("Logged out successfully")
  }

  // Show loading screen during initial auth check
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return (
      <LoginForm 
        onLogin={handleLogin}
        isLoading={authLoading}
        error={authError}
      />
    )
  }

  // Main application interface
  return (
    <div className="h-screen flex bg-background">
      <Sidebar
        user={user}
        sessions={sessions}
        currentSession={currentSession}
        onSessionSelect={handleSessionSelect}
        onNewSession={handleNewSession}
        onLogout={handleLogout}
        onToolSelect={handleToolSelect}
        activeTool={activeTool}
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        <ChatInterface
          currentSession={currentSession}
          onSendMessage={handleSendMessage}
          messages={messages}
          isLoading={isLoadingMessages}
        />
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
      <Toaster />
    </AuthProvider>
  )
}

export default App
