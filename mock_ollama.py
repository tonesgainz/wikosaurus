"""
Mock Ollama service for testing when Ollama is not available
This allows testing of the application logic without requiring Ollama to be running
"""

import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MockOllamaClient:
    """Mock Ollama client that simulates responses"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.mock_responses = {
            "general": "I'm a helpful AI assistant for Wiko cutlery employees. I can help with document analysis, translations, email responses, and complaint handling. How can I assist you today?",
            
            "pdf_analysis": """Based on the document analysis:

**Document Summary:**
This appears to be a business report containing sales data, customer feedback, and contact information for Wiko Cutlery.

**Key Business Insights:**
- Revenue performance shows strong Q4 results at $125,000
- Low complaint rate (only 3 complaints) indicates good product quality
- New product launch suggests business expansion
- Positive customer feedback highlights product durability

**Important Data Points:**
- Financial: $125,000 Q4 revenue
- Customer satisfaction: Positive feedback on quality and durability
- Product development: Premium Chef Knife Set launch

**Recommended Actions:**
1. Continue monitoring customer feedback for the new product line
2. Investigate the 3 complaints to prevent future issues
3. Leverage positive testimonials in marketing materials
4. Consider expanding the premium product line based on Q4 success""",
            
            "translation": {
                "german": "Vielen Dank für Ihren Kauf. Ihre Bestellung wird innerhalb von 2 Werktagen versandt.",
                "french": "Merci pour votre achat. Votre commande sera expédiée dans les 2 jours ouvrables.",
                "english": "Thank you for your purchase. Your order will be shipped within 2 business days."
            },
            
            "email_assistance": """Subject: Re: Your Recent Experience with Wiko Cutlery

Dear Valued Customer,

Thank you for taking the time to share your concerns about your recent Wiko Cutlery purchase. We sincerely apologize for any inconvenience you've experienced.

At Wiko Cutlery, we take great pride in the quality and durability of our products. Your feedback is invaluable in helping us maintain our high standards.

To resolve this matter promptly, I would like to offer the following solutions:

1. **Immediate Replacement**: We'll send you a replacement product at no charge
2. **Quality Inspection**: Our team will review your specific product batch
3. **Care Instructions**: We'll provide detailed maintenance guidelines

Please reply with your order number and preferred shipping address, and we'll process your replacement within 24 hours.

We value your business and want to ensure you have the exceptional Wiko Cutlery experience you deserve.

Best regards,

Customer Service Team
Wiko Cutlery Inc.
Email: support@wiko-cutlery.com
Phone: (555) 123-4567""",
            
            "complaint_handling": """**Complaint Analysis Report**

**Issue Severity:** Medium
- Product quality concern requiring immediate attention
- Customer satisfaction at risk

**Main Concerns Identified:**
1. Product durability (knife becoming dull quickly)
2. Construction quality (loose handle)
3. Customer expectations not met

**Recommended Response Strategy:**
1. **Immediate Acknowledgment**: Respond within 2 hours
2. **Empathetic Approach**: Acknowledge frustration and apologize
3. **Solution-Focused**: Offer replacement and quality assurance

**Suggested Resolution Steps:**
1. Offer immediate product replacement
2. Provide care and maintenance instructions
3. Follow up after replacement to ensure satisfaction
4. Document issue for quality control review

**Empathy Points to Address:**
- Acknowledge the inconvenience caused
- Validate their expectations for quality
- Express commitment to making it right

**Escalation Recommendations:**
- If customer remains unsatisfied after replacement, escalate to manager
- Consider offering additional compensation (discount on future purchase)

**Follow-up Actions:**
1. Send replacement within 24-48 hours
2. Follow up call/email after 1 week
3. Quality control review of product batch
4. Update care instructions if needed"""
        }
    
    def is_available(self) -> bool:
        """Mock availability check - always returns True for testing"""
        return True
    
    def list_models(self) -> List[Dict]:
        """Mock model list"""
        return [
            {"name": "llama3:8b", "size": 4661224676},
            {"name": "mistral:7b", "size": 4109865159}
        ]
    
    def pull_model(self, model_name: str) -> bool:
        """Mock model pull - always succeeds"""
        return True
    
    def generate_response(
        self, 
        model: str, 
        prompt: str, 
        system_message: Optional[str] = None,
        context: Optional[List] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict:
        """Generate mock response based on prompt content"""
        
        # Simulate processing time
        time.sleep(0.5)
        
        prompt_lower = prompt.lower()
        
        # Determine response type based on prompt content
        if any(word in prompt_lower for word in ['translate', 'german', 'french', 'übersetzen']):
            if 'german' in prompt_lower or 'deutsch' in prompt_lower:
                response_text = self.mock_responses["translation"]["german"]
            elif 'french' in prompt_lower or 'français' in prompt_lower:
                response_text = self.mock_responses["translation"]["french"]
            else:
                response_text = self.mock_responses["translation"]["english"]
        elif any(word in prompt_lower for word in ['analyze', 'document', 'pdf', 'business']):
            response_text = self.mock_responses["pdf_analysis"]
        elif any(word in prompt_lower for word in ['email', 'response', 'customer', 'letter']):
            response_text = self.mock_responses["email_assistance"]
        elif any(word in prompt_lower for word in ['complaint', 'issue', 'problem', 'dissatisfied']):
            response_text = self.mock_responses["complaint_handling"]
        else:
            response_text = self.mock_responses["general"]
        
        return {
            "model": model,
            "created_at": "2025-01-30T12:00:00Z",
            "response": response_text,
            "done": True,
            "total_duration": 500000000,
            "load_duration": 100000000,
            "prompt_eval_count": len(prompt.split()),
            "prompt_eval_duration": 50000000,
            "eval_count": len(response_text.split()),
            "eval_duration": 400000000
        }
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict:
        """Generate mock chat completion"""
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Use generate_response logic
        response_data = self.generate_response(
            model=model,
            prompt=user_message,
            temperature=temperature,
            stream=stream
        )
        
        # Convert to chat format
        return {
            "model": model,
            "created_at": response_data["created_at"],
            "message": {
                "role": "assistant",
                "content": response_data["response"]
            },
            "done": True,
            "total_duration": response_data["total_duration"],
            "load_duration": response_data["load_duration"],
            "prompt_eval_count": response_data["prompt_eval_count"],
            "prompt_eval_duration": response_data["prompt_eval_duration"],
            "eval_count": response_data["eval_count"],
            "eval_duration": response_data["eval_duration"]
        }

class MockChatbotService:
    """Mock chatbot service using MockOllamaClient"""
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.ollama = MockOllamaClient()
        self.model_name = model_name
        self.system_prompts = {
            "general": "You are a helpful AI assistant for Wiko cutlery employees.",
            "pdf_analysis": "You are an expert document analyst.",
            "translation": "You are a professional translator.",
            "email_assistance": "You are an expert in customer service communications.",
            "complaint_handling": "You are a customer service expert specializing in complaint resolution."
        }
    
    def get_response(
        self, 
        message: str, 
        context_type: str = "general",
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> Dict:
        """Get a mock response from the chatbot"""
        
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

