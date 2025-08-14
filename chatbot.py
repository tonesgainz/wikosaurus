from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
import logging

from src.models.employee import Employee, ChatSession, ChatMessage, UploadedDocument, db
from src.services.ollama_client import ChatbotService
from src.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize services using service configuration
from src.utils.service_config import service_config
chatbot_service = service_config.get_chatbot_service()
pdf_processor = PDFProcessor()
translation_service = service_config.get_translation_service(chatbot_service)
email_service = service_config.get_email_service(chatbot_service)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_employee():
    """Get current logged-in employee"""
    employee_id = session.get('employee_id')
    if employee_id:
        return Employee.query.get(employee_id)
    return None

@chatbot_bp.route('/auth/login', methods=['POST'])
def login():
    """Employee login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    employee = Employee.query.filter_by(username=username).first()
    
    if employee and employee.check_password(password) and employee.is_active:
        session['employee_id'] = employee.id
        employee.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'employee': employee.to_dict()
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@chatbot_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Employee logout"""
    session.pop('employee_id', None)
    return jsonify({'success': True})

@chatbot_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    employee = get_current_employee()
    if employee:
        return jsonify({
            'authenticated': True,
            'employee': employee.to_dict()
        })
    else:
        return jsonify({'authenticated': False})

@chatbot_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get chat sessions for current employee"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    sessions = ChatSession.query.filter_by(
        employee_id=employee.id,
        is_active=True
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return jsonify([session.to_dict() for session in sessions])

@chatbot_bp.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    """Create new chat session"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    session_name = data.get('session_name', f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    chat_session = ChatSession(
        employee_id=employee.id,
        session_name=session_name
    )
    
    db.session.add(chat_session)
    db.session.commit()
    
    return jsonify(chat_session.to_dict()), 201

@chatbot_bp.route('/chat/sessions/<int:session_id>/messages', methods=['GET'])
def get_chat_messages(session_id):
    """Get messages for a chat session"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chat_session = ChatSession.query.filter_by(
        id=session_id,
        employee_id=employee.id
    ).first()
    
    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404
    
    messages = ChatMessage.query.filter_by(
        session_id=session_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return jsonify([message.to_dict() for message in messages])

@chatbot_bp.route('/chat/sessions/<int:session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send message to chatbot"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chat_session = ChatSession.query.filter_by(
        id=session_id,
        employee_id=employee.id
    ).first()
    
    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    context_type = data.get('context_type', 'general')
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        message_type='user',
        content=user_message
    )
    db.session.add(user_msg)
    
    # Get conversation history for context
    recent_messages = ChatMessage.query.filter_by(
        session_id=session_id
    ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
    
    conversation_history = []
    for msg in reversed(recent_messages):
        role = "user" if msg.message_type == "user" else "assistant"
        conversation_history.append({
            "role": role,
            "content": msg.content
        })
    
    # Get AI response
    try:
        ai_response = chatbot_service.get_response(
            message=user_message,
            context_type=context_type,
            conversation_history=conversation_history
        )
        
        if 'error' in ai_response:
            response_content = ai_response.get('response', 'Sorry, I encountered an error.')
        else:
            # Handle different response formats
            if 'message' in ai_response:
                response_content = ai_response['message']['content']
            else:
                response_content = ai_response.get('response', 'No response generated.')
        
        # Save AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            message_type='assistant',
            content=response_content
        )
        db.session.add(ai_msg)
        
        # Update session timestamp
        chat_session.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'user_message': user_msg.to_dict(),
            'ai_response': ai_msg.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to generate response'}), 500

@chatbot_bp.route('/upload/pdf', methods=['POST'])
def upload_pdf():
    """Upload and analyze PDF document"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Create upload directory
        upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Process PDF
        pdf_summary = pdf_processor.get_document_summary(file_path)
        
        if not pdf_summary['valid']:
            os.remove(file_path)  # Clean up invalid file
            return jsonify({'error': pdf_summary['error']}), 400
        
        # Analyze business content
        business_analysis = pdf_processor.analyze_business_content(pdf_summary['full_text'])
        
        # Generate AI analysis
        analysis_prompt = f"""
        Please analyze this PDF document and provide business insights:
        
        Document Info:
        - Pages: {pdf_summary['file_info']['page_count']}
        - Words: {pdf_summary['file_info']['word_count']}
        
        Content Preview:
        {pdf_summary['text_preview']}
        
        Extracted Business Data:
        - Dates found: {', '.join(business_analysis['dates'][:5])}
        - Amounts found: {', '.join(business_analysis['amounts'][:5])}
        - Companies mentioned: {', '.join(business_analysis['companies'][:5])}
        - Key terms: {', '.join(business_analysis['key_terms'][:10])}
        
        Please provide:
        1. Document summary
        2. Key business insights
        3. Important data points
        4. Recommended actions or follow-ups
        """
        
        ai_analysis = chatbot_service.get_response(
            message=analysis_prompt,
            context_type="pdf_analysis"
        )
        
        analysis_summary = ai_analysis.get('response', 'Analysis completed')
        if 'message' in ai_analysis:
            analysis_summary = ai_analysis['message']['content']
        
        # Save document record
        document = UploadedDocument(
            employee_id=employee.id,
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=pdf_summary['file_info']['file_size'],
            mime_type='application/pdf',
            expires_at=datetime.utcnow() + timedelta(days=30),
            analysis_summary=analysis_summary
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document': document.to_dict(),
            'pdf_info': pdf_summary['file_info'],
            'business_analysis': business_analysis,
            'ai_analysis': analysis_summary
        })
        
    except Exception as e:
        logger.error(f"Error processing PDF upload: {e}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Failed to process PDF'}), 500

@chatbot_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get uploaded documents for current employee"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    documents = UploadedDocument.query.filter_by(
        employee_id=employee.id
    ).filter(
        UploadedDocument.expires_at > datetime.utcnow()
    ).order_by(UploadedDocument.uploaded_at.desc()).all()
    
    return jsonify([doc.to_dict() for doc in documents])

@chatbot_bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate text between supported languages"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    text = data.get('text', '').strip()
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'en')
    
    if not text:
        return jsonify({'error': 'Text to translate is required'}), 400
    
    try:
        result = translation_service.translate(text, source_lang, target_lang)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'error': result.get('error', 'Translation failed')}), 500
        
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({'error': 'Translation failed'}), 500

@chatbot_bp.route('/email/generate', methods=['POST'])
def generate_email():
    """Generate email response"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    email_type = data.get('email_type', 'general_response')
    customer_message = data.get('customer_message', '')
    customer_name = data.get('customer_name', '')
    order_number = data.get('order_number', '')
    product_name = data.get('product_name', '')
    additional_context = data.get('context', '')
    
    if email_type in ['complaint_response', 'general_response'] and not customer_message:
        return jsonify({'error': 'Customer message is required for responses'}), 400
    
    try:
        result = email_service.generate_email_response(
            customer_message=customer_message,
            email_type=email_type,
            customer_name=customer_name,
            order_number=order_number,
            product_name=product_name,
            additional_context=additional_context
        )
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'error': result.get('error', 'Email generation failed')}), 500
        
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        return jsonify({'error': 'Email generation failed'}), 500

@chatbot_bp.route('/complaint/analyze', methods=['POST'])
def analyze_complaint():
    """Analyze customer complaint and provide handling suggestions"""
    employee = get_current_employee()
    if not employee:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    complaint_text = data.get('complaint_text', '').strip()
    
    if not complaint_text:
        return jsonify({'error': 'Complaint text is required'}), 400
    
    analysis_prompt = f"""
    Analyze this customer complaint and provide handling recommendations:
    
    Complaint:
    {complaint_text}
    
    Please provide:
    1. Issue severity assessment (Low/Medium/High/Critical)
    2. Main concerns identified
    3. Recommended response strategy
    4. Suggested resolution steps
    5. Empathy points to address
    6. Escalation recommendations if needed
    7. Follow-up actions
    
    Focus on turning this negative experience into a positive outcome for Wiko cutlery.
    """
    
    try:
        ai_response = chatbot_service.get_response(
            message=analysis_prompt,
            context_type="complaint_handling"
        )
        
        analysis = ai_response.get('response', 'Analysis failed')
        if 'message' in ai_response:
            analysis = ai_response['message']['content']
        
        return jsonify({
            'success': True,
            'complaint_text': complaint_text,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing complaint: {e}")
        return jsonify({'error': 'Complaint analysis failed'}), 500

@chatbot_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = service_config.check_service_health()
    
    status_code = 200
    if health_status["overall"] == "degraded":
        status_code = 206  # Partial Content
    elif health_status["overall"] == "unhealthy":
        status_code = 503  # Service Unavailable
    
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    return jsonify(health_status), status_code

