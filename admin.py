from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.employee import db, Employee, ChatSession, ChatMessage, SystemSettings
from src.routes.auth import require_admin
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/employees', methods=['GET'])
@require_admin
def get_employees():
    """Get all employees (admin only)"""
    try:
        employees = Employee.query.all()
        return jsonify({
            'employees': [emp.to_dict() for emp in employees]
        })
    except Exception as e:
        logger.error(f"Get employees error: {str(e)}")
        return jsonify({'error': 'Failed to fetch employees'}), 500

@admin_bp.route('/employees', methods=['POST'])
@require_admin
def create_employee():
    """Create new employee (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if username or email already exists
        existing = Employee.query.filter(
            (Employee.username == data['username']) | 
            (Employee.email == data['email'])
        ).first()
        
        if existing:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create new employee
        employee = Employee(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            department=data.get('department', ''),
            is_admin=data.get('is_admin', False),
            is_active=data.get('is_active', True)
        )
        employee.set_password(data['password'])
        
        db.session.add(employee)
        db.session.commit()
        
        logger.info(f"New employee created: {employee.username}")
        
        return jsonify({
            'success': True,
            'employee': employee.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create employee error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create employee'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@require_admin
def update_employee(employee_id):
    """Update employee (admin only)"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            # Check if email is already taken by another user
            existing = Employee.query.filter(
                Employee.email == data['email'],
                Employee.id != employee_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 400
            employee.email = data['email']
        
        if 'role' in data:
            employee.role = data['role']
        
        if 'department' in data:
            employee.department = data['department']
        
        if 'is_active' in data:
            employee.is_active = data['is_active']
        
        if 'is_admin' in data:
            employee.is_admin = data['is_admin']
        
        if 'password' in data and data['password']:
            employee.set_password(data['password'])
        
        db.session.commit()
        
        logger.info(f"Employee updated: {employee.username}")
        
        return jsonify({
            'success': True,
            'employee': employee.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Update employee error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update employee'}), 500

@admin_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@require_admin
def delete_employee(employee_id):
    """Delete employee (admin only)"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Don't allow deleting the last admin
        if employee.is_admin:
            admin_count = Employee.query.filter_by(is_admin=True, is_active=True).count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last administrator'}), 400
        
        username = employee.username
        db.session.delete(employee)
        db.session.commit()
        
        logger.info(f"Employee deleted: {username}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Delete employee error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete employee'}), 500

@admin_bp.route('/stats', methods=['GET'])
@require_admin
def get_system_stats():
    """Get system statistics (admin only)"""
    try:
        # Employee statistics
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(is_active=True).count()
        admin_count = Employee.query.filter_by(is_admin=True, is_active=True).count()
        
        # Chat statistics
        total_sessions = ChatSession.query.count()
        total_messages = ChatMessage.query.count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = ChatSession.query.filter(ChatSession.created_at >= week_ago).count()
        recent_messages = ChatMessage.query.filter(ChatMessage.timestamp >= week_ago).count()
        recent_logins = Employee.query.filter(Employee.last_login >= week_ago).count()
        
        # Role distribution
        roles = db.session.query(Employee.role, db.func.count(Employee.id)).group_by(Employee.role).all()
        role_distribution = {role: count for role, count in roles}
        
        return jsonify({
            'employees': {
                'total': total_employees,
                'active': active_employees,
                'admins': admin_count,
                'role_distribution': role_distribution
            },
            'chat_activity': {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'recent_sessions': recent_sessions,
                'recent_messages': recent_messages,
                'recent_logins': recent_logins
            },
            'system': {
                'uptime': 'Available via health endpoint',
                'version': '1.0.0'
            }
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@admin_bp.route('/cleanup', methods=['POST'])
@require_admin
def cleanup_old_data():
    """Clean up old data (admin only)"""
    try:
        data = request.get_json()
        days = data.get('days', 30)  # Default to 30 days
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old chat sessions and their messages
        old_sessions = ChatSession.query.filter(ChatSession.last_activity < cutoff_date).all()
        deleted_sessions = len(old_sessions)
        deleted_messages = 0
        
        for session in old_sessions:
            deleted_messages += len(session.messages)
            db.session.delete(session)
        
        db.session.commit()
        
        logger.info(f"Cleanup completed: {deleted_sessions} sessions, {deleted_messages} messages")
        
        return jsonify({
            'success': True,
            'deleted_sessions': deleted_sessions,
            'deleted_messages': deleted_messages,
            'cutoff_date': cutoff_date.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Cleanup failed'}), 500

@admin_bp.route('/settings', methods=['GET'])
@require_admin
def get_settings():
    """Get system settings (admin only)"""
    try:
        settings = SystemSettings.query.all()
        return jsonify({
            'settings': [setting.to_dict() for setting in settings]
        })
    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return jsonify({'error': 'Failed to fetch settings'}), 500

@admin_bp.route('/settings', methods=['POST'])
@require_admin
def update_settings():
    """Update system settings (admin only)"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    key=key,
                    value=str(value),
                    description=f"Setting for {key}"
                )
                db.session.add(setting)
        
        db.session.commit()
        
        logger.info(f"Settings updated: {list(data.keys())}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update settings'}), 500

@admin_bp.route('/backup', methods=['POST'])
@require_admin
def create_backup():
    """Create database backup (admin only)"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # Get database path
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"wiko_assistant_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"Database backup created: {backup_filename}")
        
        return jsonify({
            'success': True,
            'backup_file': backup_filename,
            'backup_path': backup_path,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return jsonify({'error': 'Backup failed'}), 500

