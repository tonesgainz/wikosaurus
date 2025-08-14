import os
import openai
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI client for handling all AI interactions"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        self.model = "gpt-4"
        self.max_tokens = 2000
        self.temperature = 0.7
    
    def chat_completion(self, messages: List[Dict], tool_context: str = "general") -> str:
        """Generate chat completion with context-aware system prompts"""
        
        system_prompts = {
            "general": """You are a helpful AI assistant for Wiko Cutlery employees. 
            Provide professional, accurate, and helpful responses for business-related questions.
            Focus on customer service excellence, product knowledge, and operational efficiency.""",
            
            "pdf": """You are an expert document analyst for Wiko Cutlery. 
            Analyze business documents and provide insights including:
            - Key information extraction
            - Business implications
            - Action items and recommendations
            - Risk assessment when relevant""",
            
            "translate": """You are a professional translator specializing in business communications.
            Provide accurate translations between English, German, and French.
            Maintain professional tone and business-appropriate terminology.
            Consider cultural nuances in business contexts.""",
            
            "email": """You are a customer service expert for Wiko Cutlery.
            Generate professional, empathetic, and effective email responses.
            Focus on:
            - Customer satisfaction
            - Clear communication
            - Professional tone
            - Problem resolution""",
            
            "complaint": """You are a customer service specialist focused on complaint resolution.
            Analyze complaints and provide strategic recommendations for:
            - Response strategies
            - Empathy improvements
            - Escalation procedures
            - Prevention measures"""
        }
        
        system_prompt = system_prompts.get(tool_context, system_prompts["general"])
        
        # Prepare messages with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    def analyze_pdf_content(self, content: str, filename: str) -> Dict:
        """Analyze PDF content and extract business insights"""
        
        prompt = f"""Analyze this business document from Wiko Cutlery:

Document: {filename}
Content: {content}

Please provide a comprehensive analysis including:

1. SUMMARY: Brief overview of the document's main purpose and content
2. KEY POINTS: Important information, dates, numbers, and decisions
3. BUSINESS INSIGHTS: Implications for Wiko Cutlery operations
4. ACTION ITEMS: Recommended next steps or follow-up actions
5. RISK ASSESSMENT: Any potential issues or concerns identified

Format your response as a structured analysis that would be useful for business decision-making."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the structured response
            return {
                "summary": self._extract_section(analysis_text, "SUMMARY"),
                "key_points": self._extract_section(analysis_text, "KEY POINTS"),
                "insights": self._extract_section(analysis_text, "BUSINESS INSIGHTS"),
                "action_items": self._extract_section(analysis_text, "ACTION ITEMS"),
                "risk_assessment": self._extract_section(analysis_text, "RISK ASSESSMENT"),
                "full_analysis": analysis_text
            }
            
        except Exception as e:
            logger.error(f"PDF analysis error: {str(e)}")
            return {
                "summary": "Analysis temporarily unavailable",
                "key_points": ["Please try again in a moment"],
                "insights": ["Technical difficulties encountered"],
                "action_items": ["Retry document analysis"],
                "risk_assessment": "Unable to assess at this time",
                "full_analysis": f"Error: {str(e)}"
            }
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Translate text between supported languages"""
        
        prompt = f"""Translate the following text from {source_lang} to {target_lang}.
        
This is for business communication at Wiko Cutlery, so please:
- Maintain professional tone
- Use appropriate business terminology
- Consider cultural context for business communications
- Ensure accuracy and clarity

Text to translate: {text}

Provide only the translation without additional commentary."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            
            return {
                "translation": translation,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.95  # High confidence for GPT-4
            }
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "translation": "Translation temporarily unavailable",
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def generate_email_response(self, scenario: str, customer_message: str = "", tone: str = "professional") -> Dict:
        """Generate professional email responses for customer service"""
        
        prompt = f"""Generate a professional email response for Wiko Cutlery customer service.

Scenario: {scenario}
Customer Message: {customer_message}
Desired Tone: {tone}

Please create:
1. An appropriate subject line
2. A complete email body that is professional, empathetic, and helpful
3. Suggestions for improving the response

The email should:
- Address the customer's concerns directly
- Maintain Wiko Cutlery's professional standards
- Provide clear next steps when applicable
- Show empathy and understanding
- Be concise but thorough

Format as:
SUBJECT: [subject line]
BODY: [email content]
SUGGESTIONS: [improvement recommendations]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.7
            )
            
            email_content = response.choices[0].message.content
            
            return {
                "subject": self._extract_section(email_content, "SUBJECT"),
                "body": self._extract_section(email_content, "BODY"),
                "suggestions": self._extract_section(email_content, "SUGGESTIONS"),
                "tone": tone,
                "full_response": email_content
            }
            
        except Exception as e:
            logger.error(f"Email generation error: {str(e)}")
            return {
                "subject": "Response to Your Inquiry",
                "body": "Thank you for contacting Wiko Cutlery. We are currently experiencing technical difficulties but will respond to your inquiry as soon as possible.",
                "suggestions": ["Please try again in a moment"],
                "tone": tone,
                "error": str(e)
            }
    
    def analyze_complaint(self, complaint: str, current_response: str = "") -> Dict:
        """Analyze customer complaints and suggest improvements"""
        
        prompt = f"""Analyze this customer complaint for Wiko Cutlery and provide strategic recommendations:

Customer Complaint: {complaint}
Current Response (if any): {current_response}

Please provide:

1. COMPLAINT ANALYSIS: Type, severity, and key issues
2. RESPONSE STRATEGY: Recommended approach for addressing the complaint
3. EMPATHY IMPROVEMENTS: How to show better understanding and care
4. ESCALATION GUIDANCE: When and how to escalate if needed
5. PREVENTION MEASURES: How to prevent similar complaints
6. IMPROVED RESPONSE: A better response if current response was provided

Focus on customer satisfaction, brand protection, and operational improvements."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.6
            )
            
            analysis_content = response.choices[0].message.content
            
            return {
                "complaint_analysis": self._extract_section(analysis_content, "COMPLAINT ANALYSIS"),
                "response_strategy": self._extract_section(analysis_content, "RESPONSE STRATEGY"),
                "empathy_improvements": self._extract_section(analysis_content, "EMPATHY IMPROVEMENTS"),
                "escalation_guidance": self._extract_section(analysis_content, "ESCALATION GUIDANCE"),
                "prevention_measures": self._extract_section(analysis_content, "PREVENTION MEASURES"),
                "improved_response": self._extract_section(analysis_content, "IMPROVED RESPONSE"),
                "full_analysis": analysis_content
            }
            
        except Exception as e:
            logger.error(f"Complaint analysis error: {str(e)}")
            return {
                "complaint_analysis": "Analysis temporarily unavailable",
                "response_strategy": "Please try again in a moment",
                "empathy_improvements": "Technical difficulties encountered",
                "escalation_guidance": "Contact supervisor if urgent",
                "prevention_measures": "Unable to analyze at this time",
                "improved_response": "Please retry the analysis",
                "error": str(e)
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from structured AI response"""
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            if section_name.upper() in line.upper() and ':' in line:
                in_section = True
                # Include content after the colon on the same line
                content_after_colon = line.split(':', 1)[1].strip()
                if content_after_colon:
                    section_content.append(content_after_colon)
                continue
            elif in_section and any(keyword in line.upper() for keyword in ['SUMMARY', 'KEY POINTS', 'BUSINESS INSIGHTS', 'ACTION ITEMS', 'RISK ASSESSMENT', 'SUBJECT', 'BODY', 'SUGGESTIONS', 'COMPLAINT ANALYSIS', 'RESPONSE STRATEGY', 'EMPATHY IMPROVEMENTS', 'ESCALATION GUIDANCE', 'PREVENTION MEASURES', 'IMPROVED RESPONSE']):
                # Hit another section, stop collecting
                break
            elif in_section:
                section_content.append(line.strip())
        
        result = '\n'.join(section_content).strip()
        return result if result else f"No {section_name.lower()} available"
    
    def health_check(self) -> Dict:
        """Check OpenAI service health"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return {"status": "healthy", "model": self.model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

