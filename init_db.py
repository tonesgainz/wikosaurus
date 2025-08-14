#!/usr/bin/env python3
"""
Database initialization script for Wiko Cutlery Chatbot
Creates tables and adds sample employee accounts
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.main import app
from src.models.employee import db, Employee

def init_database():
    """Initialize database with tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if we already have employees
        if Employee.query.first():
            print("Database already has employee data.")
            return
        
        # Create sample employees
        sample_employees = [
            {
                'username': 'admin',
                'email': 'admin@wiko-cutlery.com',
                'password': 'admin123',
                'department': 'Administration'
            },
            {
                'username': 'customer_service',
                'email': 'cs@wiko-cutlery.com',
                'password': 'cs123',
                'department': 'Customer Service'
            },
            {
                'username': 'sales',
                'email': 'sales@wiko-cutlery.com',
                'password': 'sales123',
                'department': 'Sales'
            },
            {
                'username': 'manager',
                'email': 'manager@wiko-cutlery.com',
                'password': 'manager123',
                'department': 'Management'
            }
        ]
        
        for emp_data in sample_employees:
            employee = Employee(
                username=emp_data['username'],
                email=emp_data['email'],
                department=emp_data['department']
            )
            employee.set_password(emp_data['password'])
            db.session.add(employee)
        
        db.session.commit()
        print(f"Created {len(sample_employees)} sample employee accounts:")
        for emp in sample_employees:
            print(f"  - {emp['username']} ({emp['department']}) - password: {emp['password']}")
        
        print("\nDatabase initialization completed!")

if __name__ == "__main__":
    init_database()

