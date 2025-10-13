import psycopg2
import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate that DATABASE_URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables. Check your .env file")

print(f"Database URL: {DATABASE_URL}")  # Optional: for debugging

# Create engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

try:

    # Create Tables from CSV file
    def save_csv_to_postgres(csv_path, table_name, db_config):
        # Read CSV into DataFrame
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows from {csv_path}")

         # Clean up column names: replace '.' and spaces with '_'
        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', col).lower() for col in df.columns]
        print("Final DataFrame columns:", df.columns.tolist())

        conn = psycopg2.connect(**db_config)
        print("Connection to PostgreSQL successful!")

        cursor = conn.cursor()

        # Create a schema
        schema_name = "ai_schema"
        create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
        cursor.execute(create_schema_sql)
        conn.commit()
        print(f"📦 Schema '{schema_name}' created or already exists.")

        # Create table dynamically (simple example)
        columns = ', '.join([f"{col} TEXT" for col in df.columns])
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}."{table_name}" (
            id SERIAL PRIMARY KEY,
            {columns}
        );
    """
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"🧱 Table '{schema_name}.{table_name}' created or already exists.")

        # Insert data
        for _, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            col_names = ', '.join([f'"{col}"' for col in df.columns])
            insert_sql = f'INSERT INTO {schema_name}."{table_name}" ({col_names}) VALUES ({placeholders});'
            cursor.execute(insert_sql, tuple(row))
        
        conn.commit()
        print(f"✅ Data inserted into '{table_name}' successfully!")
        cursor.close()
        conn.close()

        print(f"✅ Data inserted into '{table_name}' successfully!")


except psycopg2.Error as e:
    print(f"❌ Error during database operations: {e}")

finally:
    if 'cursor' in locals() and cursor:  # Check if cursor was successfully created
        cursor.close()
    if 'conn' in locals() and conn:      # Check if conn was successfully created
        conn.close()
        print("PostgreSQL connection closed.")
