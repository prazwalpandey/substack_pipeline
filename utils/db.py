import psycopg2
from datetime import datetime, timezone


def create_connection():
    """Create and return a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname='database_name',
        user='username',
        password='0000',
        host='localhost',
        port='5432'
    )
    return conn

def check_if_processed(post_url):
    """Check if the post URL has already been processed."""
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM processed WHERE post_url = %s", (post_url,))
            return cursor.fetchone() is not None

def mark_as_processed(post_url, timestamp):
    """Mark a post as processed and store timestamp and processed_at."""
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO processed (post_url, timestamp, processed_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (post_url) DO NOTHING
            """, (post_url, timestamp, datetime.now(timezone.utc)))
            conn.commit()
