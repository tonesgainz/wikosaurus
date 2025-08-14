# Wiko Cutlery Employee Assistant - API Documentation

**Version:** 1.0  
**Base URL:** `http://localhost:5000/api`  
**Authentication:** Session-based with role permissions

## Overview

The Wiko Cutlery Employee Assistant provides a RESTful API for all chatbot functionality, including authentication, chat management, PDF analysis, translation, email assistance, and complaint handling.

## Authentication Endpoints

### POST /login
Authenticate user and create session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "Administration",
    "created_at": "2025-08-06T10:30:00Z"
  }
}
```

**Response (401):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

### POST /logout
End user session.

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET /me
Get current user information.

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "role": "Administration",
  "created_at": "2025-08-06T10:30:00Z"
}
```

## Chat Management Endpoints

### GET /chat/sessions
Get user's chat sessions.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Chat 8/6/2025, 3:06:42 AM",
    "created_at": "2025-08-06T03:06:42Z",
    "last_activity": "2025-08-06T03:15:30Z",
    "message_count": 5
  }
]
```

### POST /chat/sessions
Create new chat session.

**Request Body:**
```json
{
  "name": "Customer Service Discussion"
}
```

**Response (201):**
```json
{
  "id": 2,
  "name": "Customer Service Discussion",
  "created_at": "2025-08-06T10:30:00Z",
  "last_activity": "2025-08-06T10:30:00Z",
  "message_count": 0
}
```

### GET /chat/sessions/{session_id}/messages
Get messages for a specific session.

**Response (200):**
```json
[
  {
    "id": 1,
    "session_id": 1,
    "role": "user",
    "content": "Hello, can you help me with customer service?",
    "timestamp": "2025-08-06T03:06:45Z"
  },
  {
    "id": 2,
    "session_id": 1,
    "role": "assistant",
    "content": "Hello! I'd be happy to help you with customer service tasks...",
    "timestamp": "2025-08-06T03:06:50Z"
  }
]
```

### POST /chat/sessions/{session_id}/messages
Send message to chat session.

**Request Body:**
```json
{
  "content": "How do I handle a customer complaint?",
  "tool": "general"
}
```

**Response (200):**
```json
{
  "id": 3,
  "session_id": 1,
  "role": "assistant",
  "content": "When handling customer complaints, follow these steps...",
  "timestamp": "2025-08-06T10:35:00Z"
}
```

## Business Tool Endpoints

### POST /chat
General chat interaction.

**Request Body:**
```json
{
  "message": "What are the best practices for customer communication?",
  "session_id": 1
}
```

**Response (200):**
```json
{
  "response": "Here are the best practices for customer communication...",
  "session_id": 1,
  "timestamp": "2025-08-06T10:40:00Z"
}
```

### POST /analyze-pdf
Upload and analyze PDF document.

**Request (multipart/form-data):**
- `file`: PDF file (max 50MB)
- `session_id`: Chat session ID

**Response (200):**
```json
{
  "analysis": {
    "summary": "This document contains a customer contract...",
    "key_points": [
      "Contract duration: 12 months",
      "Payment terms: Net 30",
      "Delivery schedule: Monthly"
    ],
    "insights": [
      "High-value customer with recurring orders",
      "Standard payment terms indicate good credit"
    ]
  },
  "filename": "customer_contract.pdf",
  "timestamp": "2025-08-06T10:45:00Z"
}
```

### POST /translate
Translate text between languages.

**Request Body:**
```json
{
  "text": "Hello, how can I help you today?",
  "source_language": "English",
  "target_language": "German",
  "session_id": 1
}
```

**Response (200):**
```json
{
  "translation": "Hallo, wie kann ich Ihnen heute helfen?",
  "source_language": "English",
  "target_language": "German",
  "confidence": 0.95,
  "timestamp": "2025-08-06T10:50:00Z"
}
```

### POST /generate-email
Generate professional email response.

**Request Body:**
```json
{
  "scenario": "Customer asking about delayed order",
  "customer_message": "My order is late, when will it arrive?",
  "tone": "professional",
  "session_id": 1
}
```

**Response (200):**
```json
{
  "email": {
    "subject": "Update on Your Order Status",
    "body": "Dear Valued Customer,\n\nThank you for contacting us regarding your recent order...",
    "tone": "professional",
    "suggestions": [
      "Consider offering a discount for the inconvenience",
      "Provide specific tracking information if available"
    ]
  },
  "timestamp": "2025-08-06T10:55:00Z"
}
```

### POST /analyze-complaint
Analyze customer complaint and suggest improvements.

**Request Body:**
```json
{
  "complaint": "The product arrived damaged and customer service was unhelpful",
  "current_response": "We apologize for the inconvenience. Please return the item.",
  "session_id": 1
}
```

**Response (200):**
```json
{
  "analysis": {
    "complaint_type": "Product quality and service issue",
    "severity": "high",
    "key_issues": [
      "Damaged product on arrival",
      "Poor customer service experience"
    ]
  },
  "suggestions": {
    "response_strategy": "Acknowledge both issues, take responsibility, offer immediate solution",
    "empathy_improvements": [
      "Express genuine concern for the customer's experience",
      "Acknowledge the frustration caused by both issues"
    ],
    "escalation": "Consider escalating to management due to service quality concern",
    "improved_response": "We sincerely apologize for both the damaged product and the poor service you experienced..."
  },
  "timestamp": "2025-08-06T11:00:00Z"
}
```

## System Endpoints

### GET /health
Check system health and service status.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-06T11:05:00Z",
  "services": {
    "database": "healthy",
    "ollama": "healthy",
    "translation": "healthy",
    "pdf_processor": "healthy"
  },
  "version": "1.0.0",
  "uptime": "2h 30m 15s"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format",
  "details": "Missing required field: message"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "details": "Please log in to access this endpoint"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions",
  "details": "This feature requires administrator role"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "details": "Chat session with ID 999 does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "AI service temporarily unavailable"
}
```

## Rate Limiting

- **Chat endpoints**: 60 requests per minute per user
- **File upload**: 10 requests per minute per user
- **Translation**: 100 requests per minute per user
- **Authentication**: 5 requests per minute per IP

## Data Retention

- **Chat messages**: Automatically deleted after 30 days
- **Uploaded files**: Processed and deleted immediately after analysis
- **User sessions**: Expire after 24 hours of inactivity
- **Logs**: Retained for 90 days for troubleshooting

## Security Considerations

- All endpoints require authentication except `/health`
- File uploads are validated for type and size
- Session tokens are secure and httpOnly
- CORS is configured for specific origins only
- All sensitive data is encrypted in transit and at rest

