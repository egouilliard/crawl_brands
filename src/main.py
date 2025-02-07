import os
import psycopg2

def test_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        print("✅ PostgreSQL is connected and working!")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
