import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Plus, 
  MessageSquare, 
  FileText, 
  Languages, 
  Mail, 
  AlertTriangle,
  Settings,
  LogOut,
  User,
  Clock,
  ChevronRight,
  ChefHat
} from 'lucide-react'
import { motion } from 'framer-motion'

const Sidebar = ({ 
  user, 
  sessions, 
  currentSession, 
  onSessionSelect, 
  onNewSession, 
  onLogout,
  onToolSelect,
  activeTool 
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const tools = [
    {
      id: 'chat',
      name: 'Chat Assistant',
      icon: MessageSquare,
      description: 'General conversation and help',
      color: 'bg-blue-500'
    },
    {
      id: 'pdf',
      name: 'PDF Analysis',
      icon: FileText,
      description: 'Upload and analyze documents',
      color: 'bg-green-500'
    },
    {
      id: 'translate',
      name: 'Translation',
      icon: Languages,
      description: 'Translate text between languages',
      color: 'bg-purple-500'
    },
    {
      id: 'email',
      name: 'Email Assistant',
      icon: Mail,
      description: 'Generate professional emails',
      color: 'bg-orange-500'
    },
    {
      id: 'complaints',
      name: 'Complaint Analysis',
      icon: AlertTriangle,
      description: 'Analyze and handle complaints',
      color: 'bg-red-500'
    }
  ]

  const formatSessionTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className={`h-full bg-sidebar border-r transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-80'}`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <ChefHat className="w-4 h-4 text-primary-foreground" />
            </div>
            {!isCollapsed && (
              <div className="flex-1">
                <h1 className="font-bold text-lg">Wiko Assistant</h1>
                <p className="text-xs text-muted-foreground">Employee Tools</p>
              </div>
            )}
          </div>
        </div>

        {/* User Info */}
        {!isCollapsed && user && (
          <div className="p-4 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                <User className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{user.username}</p>
                <p className="text-xs text-muted-foreground truncate">{user.department}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tools Section */}
        <div className="p-4">
          {!isCollapsed && (
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Tools</h3>
          )}
          <div className="space-y-2">
            {tools.map((tool) => {
              const IconComponent = tool.icon
              const isActive = activeTool === tool.id
              
              return (
                <Button
                  key={tool.id}
                  variant={isActive ? 'default' : 'ghost'}
                  className={`w-full justify-start h-auto p-3 ${isCollapsed ? 'px-2' : ''}`}
                  onClick={() => onToolSelect(tool.id)}
                >
                  <div className={`w-2 h-2 rounded-full ${tool.color} mr-3 ${isCollapsed ? 'mr-0' : ''}`} />
                  <IconComponent className={`w-4 h-4 ${isCollapsed ? '' : 'mr-3'}`} />
                  {!isCollapsed && (
                    <div className="flex-1 text-left">
                      <div className="font-medium text-sm">{tool.name}</div>
                      <div className="text-xs text-muted-foreground">{tool.description}</div>
                    </div>
                  )}
                </Button>
              )
            })}
          </div>
        </div>

        <Separator />

        {/* Chat Sessions */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="p-4 pb-2">
            <div className="flex items-center justify-between mb-3">
              {!isCollapsed && (
                <h3 className="text-sm font-medium text-muted-foreground">Recent Chats</h3>
              )}
              <Button
                size="sm"
                onClick={onNewSession}
                className={`${isCollapsed ? 'w-8 h-8 p-0' : 'h-8'}`}
              >
                <Plus className="w-4 h-4" />
                {!isCollapsed && <span className="ml-1">New</span>}
              </Button>
            </div>
          </div>

          <ScrollArea className="flex-1 px-4">
            <div className="space-y-2 pb-4">
              {sessions.map((session) => {
                const isActive = currentSession?.id === session.id
                
                return (
                  <motion.div
                    key={session.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant={isActive ? 'secondary' : 'ghost'}
                      className={`w-full justify-start h-auto p-3 ${isCollapsed ? 'px-2' : ''}`}
                      onClick={() => onSessionSelect(session)}
                    >
                      <MessageSquare className={`w-4 h-4 flex-shrink-0 ${isCollapsed ? '' : 'mr-3'}`} />
                      {!isCollapsed && (
                        <div className="flex-1 text-left min-w-0">
                          <div className="font-medium text-sm truncate">
                            {session.session_name}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {formatSessionTime(session.updated_at)}
                          </div>
                        </div>
                      )}
                      {!isCollapsed && isActive && (
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      )}
                    </Button>
                  </motion.div>
                )
              })}
              
              {sessions.length === 0 && !isCollapsed && (
                <div className="text-center py-8">
                  <MessageSquare className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">No chat sessions yet</p>
                  <p className="text-xs text-muted-foreground">Start a new conversation</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Footer */}
        <div className="p-4 border-t">
          <div className="space-y-2">
            <Button
              variant="ghost"
              size="sm"
              className={`w-full justify-start ${isCollapsed ? 'px-2' : ''}`}
            >
              <Settings className="w-4 h-4" />
              {!isCollapsed && <span className="ml-2">Settings</span>}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className={`w-full justify-start text-destructive hover:text-destructive ${isCollapsed ? 'px-2' : ''}`}
              onClick={onLogout}
            >
              <LogOut className="w-4 h-4" />
              {!isCollapsed && <span className="ml-2">Logout</span>}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

