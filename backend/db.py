import psycopg2
import pandas as pd
import re


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
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} ({columns});")
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