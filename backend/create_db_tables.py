from pathlib import Path
from db import save_csv_to_postgres  # adjust import


# Get the base path (project/backend)
base_dir = Path(__file__).resolve().parent

csv_file_name = "sentiment_data.csv"
order_csv_file_name = "orders.csv"

# Build path to CSV
csv_path = base_dir.parent / "data" / "processed" / csv_file_name
order_csv_path = base_dir.parent / "data" / "processed" / order_csv_file_name


# Database configuration (adjust to your local Postgres)
db_config = {
        "host": "localhost",
        "port": 5432,
        "dbname": "AI",
        "user": "postgres",
        "password": "data2025"
}

# Example call
save_csv_to_postgres(str(csv_path), "sentiment_results", db_config)
save_csv_to_postgres(str(order_csv_path), "orders", db_config)