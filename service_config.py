"""
Service configuration utility for Wiko Cutlery Chatbot
Handles switching between real and mock services based on availability
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ServiceConfig:
    """Configuration manager for chatbot services"""
    
    def __init__(self):
        self.use_mock_services = os.getenv('USE_MOCK_SERVICES', 'false').lower() == 'true'
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.preferred_model = os.getenv('OLLAMA_MODEL', 'llama3:8b')
        self.fallback_model = os.getenv('OLLAMA_FALLBACK_MODEL', 'mistral:7b')
        
    def get_chatbot_service(self):
        """Get appropriate chatbot service (real or mock)"""
        if self.use_mock_services:
            from src.services.mock_ollama import MockChatbotService
            logger.info("Using mock chatbot service")
            return MockChatbotService(self.preferred_model)
        
        # Try to use real Ollama service
        try:
            from src.services.ollama_client import OllamaClient, ChatbotService
            
            client = OllamaClient(self.ollama_url)
            if client.is_available():
                logger.info("Using real Ollama chatbot service")
                return ChatbotService(self.preferred_model)
            else:
                logger.warning("Ollama not available, falling back to mock service")
                from src.services.mock_ollama import MockChatbotService
                return MockChatbotService(self.preferred_model)
                
        except Exception as e:
            logger.error(f"Error initializing Ollama service: {e}")
            logger.info("Falling back to mock service")
            from src.services.mock_ollama import MockChatbotService
            return MockChatbotService(self.preferred_model)
    
    def get_translation_service(self, chatbot_service=None):
        """Get translation service with appropriate backend"""
        from src.services.translation_service import TranslationService
        
        if chatbot_service is None:
            chatbot_service = self.get_chatbot_service()
        
        return TranslationService(chatbot_service)
    
    def get_email_service(self, chatbot_service=None):
        """Get email template service"""
        from src.services.translation_service import EmailTemplateService
        
        if chatbot_service is None:
            chatbot_service = self.get_chatbot_service()
        
        return EmailTemplateService(chatbot_service)
    
    def check_service_health(self) -> dict:
        """Check health of all services"""
        health_status = {
            "overall": "healthy",
            "services": {}
        }
        
        # Check Ollama
        try:
            from src.services.ollama_client import OllamaClient
            client = OllamaClient(self.ollama_url)
            ollama_available = client.is_available()
            
            health_status["services"]["ollama"] = {
                "status": "healthy" if ollama_available else "unavailable",
                "url": self.ollama_url,
                "models": client.list_models() if ollama_available else []
            }
            
            if not ollama_available:
                health_status["overall"] = "degraded"
                
        except Exception as e:
            health_status["services"]["ollama"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall"] = "degraded"
        
        # Check PDF processor
        try:
            from src.services.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            # Simple validation test
            test_result = processor.analyze_business_content("Test content")
            
            health_status["services"]["pdf_processor"] = {
                "status": "healthy"
            }
        except Exception as e:
            health_status["services"]["pdf_processor"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall"] = "degraded"
        
        # Check database
        try:
            from src.models.employee import db, Employee
            # Simple query test
            employee_count = Employee.query.count()
            
            health_status["services"]["database"] = {
                "status": "healthy",
                "employee_count": employee_count
            }
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["overall"] = "unhealthy"
        
        return health_status

# Global service configuration instance
service_config = ServiceConfig()

def get_chatbot_service():
    """Convenience function to get chatbot service"""
    return service_config.get_chatbot_service()

def get_translation_service():
    """Convenience function to get translation service"""
    return service_config.get_translation_service()

def get_email_service():
    """Convenience function to get email service"""
    return service_config.get_email_service()

