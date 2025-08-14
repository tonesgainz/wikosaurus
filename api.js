// API service for communicating with the Flask backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session management
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      // Handle different response types
      const contentType = response.headers.get('content-type')
      let data
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        data = await response.text()
      }

      if (!response.ok) {
        throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`)
      }

      return data
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Authentication
  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    })
  }

  async getAuthStatus() {
    return this.request('/auth/status')
  }

  // Chat Sessions
  async getChatSessions() {
    return this.request('/chat/sessions')
  }

  async createChatSession(sessionName) {
    return this.request('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ session_name: sessionName }),
    })
  }

  async getChatMessages(sessionId) {
    return this.request(`/chat/sessions/${sessionId}/messages`)
  }

  async sendMessage(sessionId, message, contextType = 'general') {
    return this.request(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ 
        message, 
        context_type: contextType 
      }),
    })
  }

  // PDF Upload and Analysis
  async uploadPDF(file) {
    const formData = new FormData()
    formData.append('file', file)

    return this.request('/upload/pdf', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    })
  }

  async getDocuments() {
    return this.request('/documents')
  }

  // Translation
  async translateText(text, sourceLang = 'auto', targetLang = 'en') {
    return this.request('/translate', {
      method: 'POST',
      body: JSON.stringify({
        text,
        source_lang: sourceLang,
        target_lang: targetLang,
      }),
    })
  }

  // Email Generation
  async generateEmail(emailData) {
    return this.request('/email/generate', {
      method: 'POST',
      body: JSON.stringify(emailData),
    })
  }

  // Complaint Analysis
  async analyzeComplaint(complaintText) {
    return this.request('/complaint/analyze', {
      method: 'POST',
      body: JSON.stringify({ complaint_text: complaintText }),
    })
  }

  // Health Check
  async getHealth() {
    return this.request('/health')
  }
}

// Create and export a singleton instance
const apiService = new ApiService()
export default apiService

// Export individual methods for convenience
export const {
  login,
  logout,
  getAuthStatus,
  getChatSessions,
  createChatSession,
  getChatMessages,
  sendMessage,
  uploadPDF,
  getDocuments,
  translateText,
  generateEmail,
  analyzeComplaint,
  getHealth,
} = apiService

