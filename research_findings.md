# Wiko Cutlery Employee Chatbot - Research Findings

## Ollama API Integration

### Key API Endpoints
- **Generate a completion**: `POST /api/generate` - For single prompt-response interactions
- **Generate a chat completion**: `POST /api/chat` - For conversational interactions (better for chatbot)
- **List Local Models**: `GET /api/tags` - To check available models
- **Pull a Model**: `POST /api/pull` - To download models like Llama 3 or Mistral

### API Conventions
- Model names follow `model:tag` format (e.g., `llama3:8b`, `mistral:7b`)
- All durations returned in nanoseconds
- Streaming responses available (can be disabled with `{"stream": false}`)
- Default model stay-alive time: 5 minutes

### Key Parameters for Chat Applications
- `model`: Required - the model name (llama3:8b or mistral:7b for our use case)
- `prompt`: The user input
- `system`: System message to define chatbot behavior
- `context`: For maintaining conversation memory
- `format`: Can be set to "json" for structured responses
- `temperature`: Controls response creativity (0-1)
- `stream`: Boolean for streaming vs single response

### Python Integration
- Ollama runs on `localhost:11434` by default
- Simple HTTP requests using `requests` library
- Can maintain conversation context between requests
- Supports multimodal inputs (images) for models like LLaVA

Source: https://ollama.readthedocs.io/en/api/



## Flask-Ollama Integration Patterns

### Example Implementation Structure
From GitHub example (pritom007/ollama_chatbot):
- Flask app with session management for conversation history
- Routes: `/` (home), `/ask` (POST for chat interactions)
- Session storage for maintaining chat context
- Integration with external prompt processing modules
- JSON responses for frontend communication

### Key Implementation Details
- Uses Flask sessions for conversation memory
- Implements streaming and non-streaming responses
- Modular design with separate bot logic
- Session history tracking with timestamps
- Error handling for API failures

Source: https://github.com/pritom007/ollama_chatbot


## PDF Analysis Libraries

### Top Python Libraries for PDF Processing
1. **PyMuPDF (fitz)** - Recommended as best performing
   - High performance for data extraction, analysis, conversion
   - Better than PDFplumber and PyPDF2 according to community feedback
   - Supports text, images, and metadata extraction

2. **pdfplumber** - Advanced precision control
   - Built on pdfminer.six
   - Excellent for table extraction and detailed character/font information
   - Visual debugging capabilities
   - Good for structured document analysis

3. **PyPDF2/PyPDF3** - Mature and stable
   - Pure Python library
   - Good for basic text extraction and PDF manipulation
   - Limited with scanned documents

### Business Document Analysis Features Needed
- Content extraction and summarization
- Key data identification (dates, amounts, names, etc.)
- Table extraction for structured data
- Metadata analysis
- Multi-page document processing

Sources: 
- https://www.reddit.com/r/LangChain/comments/1e7cntq/whats_the_best_python_library_for_extracting_text/
- https://www.metriccoders.com/post/a-guide-to-pdf-extraction-libraries-in-python

## Translation Services Integration

### Translation API Options
1. **Google Cloud Translation API**
   - Neural machine translation technology
   - Supports 100+ languages including English, German, French
   - REST API with Python client library
   - Good for dynamic translation

2. **Azure Translator Service**
   - Cloud-based REST API with neural translation
   - Real-time text translation capabilities
   - Python client library available
   - Enterprise-grade reliability

3. **Microsoft Translator**
   - Offline capabilities
   - Document translation support
   - Integration with business applications

### Multilingual Chatbot Considerations
- Language detection for automatic translation
- Context preservation across languages
- Business terminology consistency
- Customer communication templates in multiple languages
- Internal document translation workflows

Sources:
- https://learn.microsoft.com/en-us/python/api/overview/azure/ai-translation-text-readme
- https://cloud.google.com/translate
- https://www.crescendo.ai/blog/best-multilingual-chatbots


## Business Chatbot Architecture

### Core Components for Employee Chatbots
1. **Natural Language Processing (NLP) Layer**
   - Intent recognition and entity extraction
   - Context management for multi-turn conversations
   - Language detection for multilingual support

2. **Business Logic Layer**
   - Task-specific modules (PDF analysis, translation, email generation)
   - Integration with external APIs and services
   - Workflow automation and process management

3. **Data Management Layer**
   - Conversation history storage
   - Document storage and retrieval
   - User authentication and session management
   - 30-day data retention compliance

4. **Integration Layer**
   - Email system integration
   - Document management system connectivity
   - Translation service APIs
   - Authentication systems

### Customer Service Automation Patterns
- **Complaint Handling Workflow**
  - Automatic categorization and priority assignment
  - Empathy-driven response generation
  - Escalation procedures for complex issues
  - Response time optimization

- **Email Response Generation**
  - Template-based responses for common scenarios
  - Personalized content generation
  - Multi-language support
  - Tone and style consistency

### Internal Employee Chatbot Use Cases
1. **Document Processing**
   - PDF analysis and summarization
   - Key information extraction
   - Business insights generation

2. **Communication Support**
   - Email drafting assistance
   - Translation services
   - Customer response templates

3. **Process Automation**
   - Complaint handling workflows
   - Knowledge base queries
   - Task routing and assignment

### Performance Considerations
- Response time optimization (target: <2 seconds)
- Context window management for long conversations
- Scalability for multiple concurrent users
- Error handling and fallback mechanisms

Sources:
- https://marutitech.com/chatbots-work-guide-chatbot-architecture/
- https://www.workato.com/the-connector/internal-chatbots/
- https://www.leewayhertz.com/ai-in-complaint-management/


## Recommended System Architecture for Wiko Cutlery Chatbot

### Technology Stack
- **Backend**: Flask (Python 3.11+)
- **LLM Integration**: Ollama with Llama 3:8b or Mistral:7b
- **Frontend**: React with responsive design
- **PDF Processing**: PyMuPDF (fitz) for performance
- **Translation**: Azure Translator Service or Google Cloud Translation
- **Database**: SQLite for development, PostgreSQL for production
- **Authentication**: Flask-Login with session management
- **File Storage**: Local filesystem with 30-day cleanup

### Core Features Implementation Plan

#### 1. PDF Analysis Module
```python
# Key capabilities needed:
- Text extraction using PyMuPDF
- Content summarization via Ollama
- Key data identification (dates, amounts, contacts)
- Business insights generation
- Multi-page document processing
```

#### 2. Translation Module
```python
# Integration requirements:
- Language detection
- Real-time translation for chat
- Document translation
- Context preservation
- Business terminology consistency
```

#### 3. Email Assistance Module
```python
# Features to implement:
- Template generation for common scenarios
- Draft improvement suggestions
- Tone and style optimization
- Multi-language email composition
- Customer-specific personalization
```

#### 4. Complaint Handling Module
```python
# Workflow automation:
- Issue categorization and priority
- Response time optimization
- Empathy-driven communication
- Escalation procedures
- Resolution tracking
```

### Security and Compliance
- Employee authentication system
- Session management with timeout
- Data encryption for sensitive documents
- 30-day automatic data retention cleanup
- Audit logging for business compliance

### Performance Targets
- Response time: <2 seconds for chat interactions
- File upload: Support up to 50MB PDFs
- Concurrent users: 10-20 employees simultaneously
- Uptime: 99.5% availability during business hours

### Deployment Strategy
- Local development with Ollama on Mac
- Docker containerization for consistency
- Environment-specific configuration
- Automated testing and deployment scripts

