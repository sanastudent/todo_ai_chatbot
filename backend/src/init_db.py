#!/usr/bin/env python3
"""
Database initialization script for the Todo AI Chatbot
This script creates the database tables if they don't exist
"""

import asyncio
import os
from sqlmodel import SQLModel, create_engine
from sqlalchemy import inspect
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message
from src.services.database import sync_engine

async def initialize_database():
    """Initialize the database with required tables"""
    print("Initializing database...")

    # Check if tables exist
    inspector = inspect(sync_engine)
    existing_tables = inspector.get_table_names()

    print(f"Existing tables: {existing_tables}")

    # Create tables if they don't exist
    if not existing_tables:
        print("Creating database tables...")
        SQLModel.metadata.create_all(sync_engine)
        print("Database tables created successfully!")
    else:
        print("Tables already exist.")

    # Verify tables were created
    updated_tables = inspector.get_table_names()
    print(f"Updated tables: {updated_tables}")

    # Check for our specific tables
    required_tables = ['task', 'conversation', 'message']
    missing_tables = [table for table in required_tables if table not in updated_tables]

    if missing_tables:
        print(f"ERROR: Missing tables: {missing_tables}")
        return False
    else:
        print("SUCCESS: All required tables exist!")
        return True

if __name__ == "__main__":
    success = asyncio.run(initialize_database())
    if success:
        print("\nDatabase initialization completed successfully!")
    else:
        print("\nDatabase initialization failed!")
        exit(1)