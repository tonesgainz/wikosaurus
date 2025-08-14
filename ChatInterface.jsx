import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Send, 
  Bot, 
  User, 
  FileText, 
  Languages, 
  Mail, 
  AlertTriangle,
  Loader2,
  MessageSquare
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const ChatInterface = ({ currentSession, onSendMessage, messages, isLoading }) => {
  const [inputMessage, setInputMessage] = useState('')
  const [contextType, setContextType] = useState('general')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || isLoading) return

    await onSendMessage(inputMessage, contextType)
    setInputMessage('')
    inputRef.current?.focus()
  }

  const contextTypes = [
    { value: 'general', label: 'General', icon: MessageSquare, color: 'bg-blue-500' },
    { value: 'pdf_analysis', label: 'PDF Analysis', icon: FileText, color: 'bg-green-500' },
    { value: 'translation', label: 'Translation', icon: Languages, color: 'bg-purple-500' },
    { value: 'email_assistance', label: 'Email Help', icon: Mail, color: 'bg-orange-500' },
    { value: 'complaint_handling', label: 'Complaints', icon: AlertTriangle, color: 'bg-red-500' }
  ]

  const getMessageIcon = (type) => {
    return type === 'user' ? User : Bot
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b bg-card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              {currentSession?.session_name || 'New Chat'}
            </h2>
            <p className="text-sm text-muted-foreground">
              Wiko Cutlery Employee Assistant
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {contextTypes.find(ct => ct.value === contextType)?.label}
            </Badge>
          </div>
        </div>
      </div>

      {/* Context Type Selector */}
      <div className="p-3 border-b bg-muted/30">
        <div className="flex flex-wrap gap-2">
          {contextTypes.map((type) => {
            const IconComponent = type.icon
            return (
              <Button
                key={type.value}
                variant={contextType === type.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setContextType(type.value)}
                className="text-xs h-8"
              >
                <IconComponent className="w-3 h-3 mr-1" />
                {type.label}
              </Button>
            )
          })}
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          <AnimatePresence>
            {messages.map((message, index) => {
              const IconComponent = getMessageIcon(message.message_type)
              const isUser = message.message_type === 'user'
              
              return (
                <motion.div
                  key={message.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                        <IconComponent className="w-4 h-4 text-primary-foreground" />
                      </div>
                    </div>
                  )}
                  
                  <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
                    <Card className={`${isUser ? 'bg-primary text-primary-foreground' : 'bg-card'}`}>
                      <CardContent className="p-3">
                        <div className="whitespace-pre-wrap text-sm">
                          {message.content}
                        </div>
                        <div className={`text-xs mt-2 ${isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                          {formatTimestamp(message.timestamp)}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {isUser && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                        <IconComponent className="w-4 h-4 text-secondary-foreground" />
                      </div>
                    </div>
                  )}
                </motion.div>
              )
            })}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3 justify-start"
            >
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary-foreground" />
                </div>
              </div>
              <Card className="bg-card">
                <CardContent className="p-3">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Thinking...
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Message Input */}
      <div className="p-4 border-t bg-card">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder={`Ask about ${contextTypes.find(ct => ct.value === contextType)?.label.toLowerCase()}...`}
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            type="submit" 
            disabled={!inputMessage.trim() || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
        
        <div className="mt-2 text-xs text-muted-foreground">
          Current mode: <span className="font-medium">
            {contextTypes.find(ct => ct.value === contextType)?.label}
          </span>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

