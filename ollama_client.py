import requests
import json
import logging
from typing import Dict, List, Optional, Generator

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            response = requests.get(f"{self.api_url}/tags")
            response.raise_for_status()
            return response.json().get('models', [])
        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model if not available"""
        try:
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": model_name},
                stream=True
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def generate_response(
        self, 
        model: str, 
        prompt: str, 
        system_message: Optional[str] = None,
        context: Optional[List] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict:
        """Generate a response using Ollama"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_message:
            payload["system"] = system_message
            
        if context:
            payload["context"] = context
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                return response.json()
                
        except requests.RequestException as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "error": str(e),
                "response": "I'm sorry, I'm having trouble connecting to the AI service. Please try again later."
            }
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict:
        """Generate a chat completion using Ollama"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                return response.json()
                
        except requests.RequestException as e:
            logger.error(f"Failed to generate chat completion: {e}")
            return {
                "error": str(e),
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, I'm having trouble connecting to the AI service. Please try again later."
                }
            }
    
    def _handle_streaming_response(self, response) -> Generator[Dict, None, None]:
        """Handle streaming response from Ollama"""
        for line in response.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                except json.JSONDecodeError:
                    continue

class ChatbotService:
    def __init__(self, model_name: str = "llama3:8b"):
        self.ollama = OllamaClient()
        self.model_name = model_name
        self.system_prompts = {
            "general": """You are a helpful AI assistant for Wiko cutlery employees. You help with:
1. Analyzing PDF documents and extracting business insights
2. Translating content between English, German, and French
3. Generating professional email responses to customers
4. Providing suggestions for improving customer complaint handling

Always be professional, helpful, and concise in your responses. When handling customer service scenarios, emphasize empathy and solution-oriented approaches.""",
            
            "pdf_analysis": """You are an expert document analyst. Analyze the provided PDF content and:
1. Summarize the key points
2. Identify important business data (dates, amounts, contacts, etc.)
3. Extract actionable insights
4. Highlight any issues or concerns that need attention

Provide your analysis in a clear, structured format.""",
            
            "translation": """You are a professional translator specializing in business communications. 
Translate the provided text accurately while maintaining:
1. Professional tone and context
2. Business terminology consistency
3. Cultural appropriateness
4. Original meaning and intent

Provide only the translation unless specifically asked for additional context.""",
            
            "email_assistance": """You are an expert in customer service communications. Help create professional email responses that:
1. Address the customer's concerns directly
2. Maintain a helpful and empathetic tone
3. Provide clear solutions or next steps
4. Follow business communication best practices
5. Are appropriate for the cutlery/kitchenware industry

Consider the customer's situation and provide personalized, solution-oriented responses.""",
            
            "complaint_handling": """You are a customer service expert specializing in complaint resolution. Analyze the complaint and provide:
1. Assessment of the issue severity and urgency
2. Recommended response strategy
3. Suggested resolution steps
4. Tips for empathetic communication
5. Escalation procedures if needed

Focus on turning negative experiences into positive outcomes while protecting the company's reputation."""
        }
    
    def get_response(
        self, 
        message: str, 
        context_type: str = "general",
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> Dict:
        """Get a response from the chatbot"""
        
        if not self.ollama.is_available():
            return {
                "error": "Ollama service is not available",
                "response": "I'm sorry, the AI service is currently unavailable. Please check that Ollama is running and try again."
            }
        
        system_message = self.system_prompts.get(context_type, self.system_prompts["general"])
        
        if conversation_history:
            # Use chat completion for conversation context
            messages = [{"role": "system", "content": system_message}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            
            return self.ollama.chat_completion(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
        else:
            # Use simple generation for single queries
            return self.ollama.generate_response(
                model=self.model_name,
                prompt=message,
                system_message=system_message,
                temperature=temperature
            )

