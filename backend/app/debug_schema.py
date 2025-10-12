#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://forge:forge@postgres:5432/forge")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check projects table structure
        result = conn.execute(text("SELECT * FROM projects LIMIT 1"))
        if result.rowcount > 0:
            row = result.fetchone()
            print("Sample project row:")
            for i, column in enumerate(result.keys()):
                print(f"  {column}: {row[i]} (type: {type(row[i])})")
        else:
            print("No projects found in database")
            
        # Check table schema
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'projects'
            ORDER BY ordinal_position
        """))
        print("\nTable schema:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
            
except Exception as e:
    print(f"Error: {e}")
