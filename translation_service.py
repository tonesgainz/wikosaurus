import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Translation service that can use multiple backends:
    1. AI-based translation (using Ollama)
    2. Google Translate API (if configured)
    3. Azure Translator (if configured)
    """
    
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client
        self.supported_languages = {
            'en': 'English',
            'de': 'German', 
            'fr': 'French',
            'auto': 'Auto-detect'
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        # Simple heuristic-based detection
        text_lower = text.lower()
        
        # German indicators
        german_words = ['der', 'die', 'das', 'und', 'ist', 'mit', 'für', 'von', 'auf', 'zu', 'ich', 'sie', 'wir']
        german_score = sum(1 for word in german_words if word in text_lower)
        
        # French indicators  
        french_words = ['le', 'la', 'les', 'et', 'est', 'avec', 'pour', 'de', 'sur', 'à', 'je', 'il', 'nous']
        french_score = sum(1 for word in french_words if word in text_lower)
        
        # English indicators
        english_words = ['the', 'and', 'is', 'with', 'for', 'of', 'on', 'to', 'i', 'you', 'we', 'they']
        english_score = sum(1 for word in english_words if word in text_lower)
        
        scores = {'en': english_score, 'de': german_score, 'fr': french_score}
        detected = max(scores, key=scores.get)
        
        # If no clear winner, default to English
        if scores[detected] == 0:
            return 'en'
        
        return detected
    
    def translate_with_ai(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Translate using AI (Ollama)"""
        if not self.ollama_client:
            return {"error": "AI translation service not available"}
        
        # Map language codes to full names
        source_name = self.supported_languages.get(source_lang, source_lang)
        target_name = self.supported_languages.get(target_lang, target_lang)
        
        if source_lang == 'auto':
            detected_lang = self.detect_language(text)
            source_name = self.supported_languages.get(detected_lang, 'English')
        
        prompt = f"""
        Translate the following text from {source_name} to {target_name}.
        Maintain professional tone and business context.
        Preserve any technical terms related to cutlery, kitchenware, or business.
        
        Text to translate:
        {text}
        
        Translation:
        """
        
        try:
            response = self.ollama_client.get_response(
                message=prompt,
                context_type="translation",
                temperature=0.3  # Lower temperature for more consistent translations
            )
            
            if 'error' in response:
                return {"error": response['error']}
            
            translated_text = response.get('response', text)
            if 'message' in response:
                translated_text = response['message']['content']
            
            # Clean up the translation (remove any extra explanations)
            lines = translated_text.strip().split('\n')
            # Take the first non-empty line as the translation
            for line in lines:
                line = line.strip()
                if line and not line.startswith('Translation:') and not line.startswith('Here'):
                    translated_text = line
                    break
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "method": "ai"
            }
            
        except Exception as e:
            logger.error(f"AI translation error: {e}")
            return {"error": f"Translation failed: {str(e)}"}
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> Dict:
        """Main translation method"""
        if not text.strip():
            return {"error": "Empty text provided"}
        
        if source_lang == target_lang:
            return {
                "success": True,
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "method": "no_translation_needed"
            }
        
        # Validate language codes
        if target_lang not in self.supported_languages:
            return {"error": f"Unsupported target language: {target_lang}"}
        
        if source_lang != 'auto' and source_lang not in self.supported_languages:
            return {"error": f"Unsupported source language: {source_lang}"}
        
        # Use AI translation as primary method
        return self.translate_with_ai(text, source_lang, target_lang)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()

class EmailTemplateService:
    """Service for generating email templates and responses"""
    
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client
        self.templates = {
            'complaint_response': {
                'subject': 'Re: Your Recent Experience with Wiko Cutlery',
                'tone': 'empathetic and solution-oriented'
            },
            'warranty_inquiry': {
                'subject': 'Wiko Cutlery Warranty Information',
                'tone': 'informative and helpful'
            },
            'product_inquiry': {
                'subject': 'Wiko Cutlery Product Information',
                'tone': 'enthusiastic and informative'
            },
            'order_status': {
                'subject': 'Your Wiko Cutlery Order Status',
                'tone': 'professional and reassuring'
            },
            'thank_you': {
                'subject': 'Thank You for Choosing Wiko Cutlery',
                'tone': 'grateful and warm'
            }
        }
    
    def generate_email_response(
        self, 
        customer_message: str, 
        email_type: str = 'general_response',
        customer_name: str = '',
        order_number: str = '',
        product_name: str = '',
        additional_context: str = ''
    ) -> Dict:
        """Generate a complete email response"""
        
        if not self.ollama_client:
            return {"error": "Email generation service not available"}
        
        template_info = self.templates.get(email_type, {
            'subject': 'Re: Your Inquiry',
            'tone': 'professional and helpful'
        })
        
        # Build context information
        context_parts = []
        if customer_name:
            context_parts.append(f"Customer name: {customer_name}")
        if order_number:
            context_parts.append(f"Order number: {order_number}")
        if product_name:
            context_parts.append(f"Product: {product_name}")
        if additional_context:
            context_parts.append(f"Additional context: {additional_context}")
        
        context_str = "\n".join(context_parts) if context_parts else "No additional context provided"
        
        prompt = f"""
        Generate a professional email response for Wiko Cutlery customer service.
        
        Customer Message:
        {customer_message}
        
        Context Information:
        {context_str}
        
        Email Type: {email_type}
        Tone: {template_info['tone']}
        Suggested Subject: {template_info['subject']}
        
        Requirements:
        1. Address the customer's specific concerns
        2. Maintain {template_info['tone']} tone
        3. Include appropriate Wiko Cutlery branding
        4. Provide clear next steps or solutions
        5. Include professional closing
        6. Be specific to the cutlery/kitchenware industry
        
        Generate a complete email with:
        - Subject line
        - Professional greeting
        - Body addressing the customer's needs
        - Appropriate closing
        - Signature block for Wiko Cutlery
        
        Format as:
        Subject: [subject line]
        
        [email body]
        """
        
        try:
            response = self.ollama_client.get_response(
                message=prompt,
                context_type="email_assistance",
                temperature=0.7
            )
            
            if 'error' in response:
                return {"error": response['error']}
            
            email_content = response.get('response', '')
            if 'message' in response:
                email_content = response['message']['content']
            
            # Parse subject and body
            lines = email_content.split('\n')
            subject = template_info['subject']  # Default subject
            body_lines = []
            
            for i, line in enumerate(lines):
                if line.strip().startswith('Subject:'):
                    subject = line.replace('Subject:', '').strip()
                elif i > 0 or not line.strip().startswith('Subject:'):
                    body_lines.append(line)
            
            body = '\n'.join(body_lines).strip()
            
            return {
                "success": True,
                "subject": subject,
                "body": body,
                "full_email": email_content,
                "email_type": email_type,
                "tone": template_info['tone']
            }
            
        except Exception as e:
            logger.error(f"Email generation error: {e}")
            return {"error": f"Email generation failed: {str(e)}"}
    
    def get_email_templates(self) -> Dict:
        """Get available email templates"""
        return {
            template_type: {
                'subject': info['subject'],
                'tone': info['tone'],
                'description': self._get_template_description(template_type)
            }
            for template_type, info in self.templates.items()
        }
    
    def _get_template_description(self, template_type: str) -> str:
        """Get description for template type"""
        descriptions = {
            'complaint_response': 'Response to customer complaints with empathy and solutions',
            'warranty_inquiry': 'Information about product warranties and coverage',
            'product_inquiry': 'Details about products, features, and specifications',
            'order_status': 'Updates on order processing and shipping',
            'thank_you': 'Appreciation messages for purchases and loyalty'
        }
        return descriptions.get(template_type, 'General customer service response')

