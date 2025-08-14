import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Wiko Cutlery Employee Assistant</h1>
        <p className="text-lg text-muted-foreground mb-8">
          AI-powered assistant for Wiko Cutlery employees
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">PDF Analysis</h2>
            <p className="text-muted-foreground">Upload and analyze business documents</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">Translation</h2>
            <p className="text-muted-foreground">Translate text between English, German, and French</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">Email Assistant</h2>
            <p className="text-muted-foreground">Generate professional customer responses</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">Complaint Handling</h2>
            <p className="text-muted-foreground">Analyze and improve complaint responses</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">Chat Assistant</h2>
            <p className="text-muted-foreground">General AI assistance for business tasks</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-2">Local Setup</h2>
            <p className="text-muted-foreground">Runs on Ollama for privacy and control</p>
          </div>
        </div>
        
        <div className="mt-12 text-center">
          <p className="text-sm text-muted-foreground">
            Frontend is working! Backend integration coming next...
          </p>
        </div>
      </div>
    </div>
  )
}

export default App

