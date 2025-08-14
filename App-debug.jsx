import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [debugInfo, setDebugInfo] = useState('Loading...')

  useEffect(() => {
    // Test basic functionality
    setDebugInfo('React is working!')
    
    // Test API connection
    fetch('http://localhost:5000/api/health')
      .then(response => response.json())
      .then(data => {
        setDebugInfo(`Backend connected! Status: ${data.overall}`)
      })
      .catch(error => {
        setDebugInfo(`Backend error: ${error.message}`)
      })
  }, [])

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Wiko Cutlery Employee Assistant</h1>
        <p className="text-lg text-muted-foreground mb-8">Debug Mode</p>
        
        <div className="bg-card p-6 rounded-lg border">
          <h2 className="text-xl font-semibold mb-4">Debug Information</h2>
          <p className="text-sm font-mono bg-muted p-3 rounded">
            {debugInfo}
          </p>
        </div>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">PDF Analysis</h3>
            <p className="text-muted-foreground text-sm">Upload and analyze business documents</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Translation</h3>
            <p className="text-muted-foreground text-sm">Translate text between languages</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Email Assistant</h3>
            <p className="text-muted-foreground text-sm">Generate professional responses</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

