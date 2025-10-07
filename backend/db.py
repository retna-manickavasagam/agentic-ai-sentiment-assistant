import psycopg2

try:
    conn = psycopg2.connect(
        dbname="AI",
        user="postgres",
        password="moudbpass212",
        host="localhost",
        port="5432"
    )
    print("Connection to PostgreSQL successful!")

    cursor = conn.cursor()

    # Create a schema
    schema_name = "ai_schema"
    create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    cursor.execute(create_schema_sql)
    conn.commit()
    print(f"Schema '{schema_name}' created or already exists.")

    # Create a table within the schema
    table_name = "my_table"
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INTEGER
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print(f"Table '{table_name}' created or already exists in schema '{schema_name}'.")

except psycopg2.Error as e:
    print(f"Error during database operations: {e}")

finally:
    if 'cursor' in locals() and cursor:  # Check if cursor was successfully created
        cursor.close()
    if 'conn' in locals() and conn:      # Check if conn was successfully created
        conn.close()
        print("PostgreSQL connection closed.")