#!/usr/bin/env python3
"""
Migration script to add category and due_date columns to existing task table
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Add category and due_date columns to the existing task table"""
    # Connect to the database
    conn = sqlite3.connect("todo_chatbot_dev.db")
    cursor = conn.cursor()

    try:
        # Check if category column exists
        cursor.execute("PRAGMA table_info(task)")
        columns = [column[1] for column in cursor.fetchall()]

        print(f"Current columns in task table: {columns}")

        # Add category column if it doesn't exist
        if 'category' not in columns:
            print("Adding category column...")
            cursor.execute("ALTER TABLE task ADD COLUMN category TEXT NOT NULL DEFAULT 'general'")
            print("Category column added successfully!")
        else:
            print("Category column already exists.")

        # Add due_date column if it doesn't exist
        if 'due_date' not in columns:
            print("Adding due_date column...")
            cursor.execute("ALTER TABLE task ADD COLUMN due_date TIMESTAMP")
            print("Due date column added successfully!")
        else:
            print("Due date column already exists.")

        # Verify the changes
        cursor.execute("PRAGMA table_info(task)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in task table: {updated_columns}")

        # Commit the changes
        conn.commit()
        print("Database migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()