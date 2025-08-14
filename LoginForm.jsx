import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ChefHat, Loader2, User, Lock, AlertCircle } from 'lucide-react'
import { motion } from 'framer-motion'

const LoginForm = ({ onLogin, isLoading, error }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!credentials.username || !credentials.password) return
    await onLogin(credentials)
  }

  const handleInputChange = (field, value) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const sampleAccounts = [
    { username: 'admin', department: 'Administration' },
    { username: 'customer_service', department: 'Customer Service' },
    { username: 'sales', department: 'Sales' },
    { username: 'manager', department: 'Management' }
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-lg">
          <CardHeader className="text-center space-y-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center mx-auto"
            >
              <ChefHat className="w-8 h-8 text-primary-foreground" />
            </motion.div>
            <div>
              <CardTitle className="text-2xl font-bold">Wiko Cutlery</CardTitle>
              <CardDescription className="text-base">
                Employee Assistant Portal
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={credentials.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={credentials.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className="pl-10"
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading || !credentials.username || !credentials.password}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="space-y-3">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Demo Accounts</p>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                {sampleAccounts.map((account) => (
                  <Button
                    key={account.username}
                    variant="outline"
                    size="sm"
                    className="text-xs h-auto p-2 flex flex-col items-start"
                    onClick={() => setCredentials({
                      username: account.username,
                      password: account.username + '123'
                    })}
                    disabled={isLoading}
                  >
                    <span className="font-medium">{account.username}</span>
                    <span className="text-muted-foreground">{account.department}</span>
                  </Button>
                ))}
              </div>
              
              <p className="text-xs text-center text-muted-foreground">
                Click any demo account to auto-fill credentials
              </p>
            </div>
          </CardContent>
        </Card>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-muted-foreground">
            AI-powered assistant for Wiko Cutlery employees
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            PDF analysis • Translation • Email assistance • Complaint handling
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default LoginForm

