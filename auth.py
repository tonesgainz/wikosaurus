from flask import Blueprint, request, jsonify, session
from datetime import datetime
from src.models.employee import db, Employee
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Employee login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find employee by username
        employee = Employee.query.filter_by(username=username).first()
        
        if not employee:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        if not employee.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated. Please contact administrator.'
            }), 401
        
        if not employee.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Update last login
        employee.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['employee_id'] = employee.id
        session['username'] = employee.username
        session['is_admin'] = employee.is_admin
        
        logger.info(f"Employee {username} logged in successfully")
        
        return jsonify({
            'success': True,
            'user': employee.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed due to server error'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Employee logout endpoint"""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        
        logger.info(f"Employee {username} logged out")
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        employee_id = session.get('employee_id')
        
        if not employee_id:
            return jsonify({
                'error': 'Not authenticated'
            }), 401
        
        employee = Employee.query.get(employee_id)
        
        if not employee or not employee.is_active:
            session.clear()
            return jsonify({
                'error': 'User not found or deactivated'
            }), 401
        
        return jsonify(employee.to_dict())
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'Failed to get user information'
        }), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user session is valid"""
    try:
        employee_id = session.get('employee_id')
        
        if not employee_id:
            return jsonify({
                'authenticated': False
            })
        
        employee = Employee.query.get(employee_id)
        
        if not employee or not employee.is_active:
            session.clear()
            return jsonify({
                'authenticated': False
            })
        
        return jsonify({
            'authenticated': True,
            'user': employee.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Session check error: {str(e)}")
        return jsonify({
            'authenticated': False,
            'error': 'Session check failed'
        }), 500

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        employee_id = session.get('employee_id')
        
        if not employee_id:
            return jsonify({
                'error': 'Authentication required'
            }), 401
        
        employee = Employee.query.get(employee_id)
        
        if not employee or not employee.is_active:
            session.clear()
            return jsonify({
                'error': 'User not found or deactivated'
            }), 401
        
        # Add employee to request context
        request.current_employee = employee
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin privileges"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        employee_id = session.get('employee_id')
        
        if not employee_id:
            return jsonify({
                'error': 'Authentication required'
            }), 401
        
        employee = Employee.query.get(employee_id)
        
        if not employee or not employee.is_active:
            session.clear()
            return jsonify({
                'error': 'User not found or deactivated'
            }), 401
        
        if not employee.is_admin:
            return jsonify({
                'error': 'Administrator privileges required'
            }), 403
        
        # Add employee to request context
        request.current_employee = employee
        
        return f(*args, **kwargs)
    
    return decorated_function

