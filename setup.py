#!/usr/bin/env python
"""
Setup script to create initial admin user
Run this after migrations: python setup.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accorix.settings')
django.setup()

from core.models import User

def create_admin():
    print("Creating admin user...")
    print("Please provide the following information:")
    
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    login_id = input("Login ID (6-12 characters): ")
    email = input("Email: ")
    password = input("Password (min 8 chars, with uppercase, lowercase, special char): ")
    
    if len(login_id) < 6 or len(login_id) > 12:
        print("Error: Login ID must be between 6-12 characters")
        return
    
    if User.objects.filter(login_id=login_id).exists():
        print("Error: Login ID already exists")
        return
    
    if User.objects.filter(email=email).exists():
        print("Error: Email already exists")
        return
    
    try:
        user = User.objects.create_user(
            username=login_id,
            login_id=login_id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        print(f"Admin user created successfully: {user.login_id}")
    except Exception as e:
        print(f"Error creating user: {e}")

if __name__ == '__main__':
    create_admin()
