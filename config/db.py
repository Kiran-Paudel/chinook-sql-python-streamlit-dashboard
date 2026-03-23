from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load variables from .env file into environment
load_dotenv()

def get_engine():
    """
    Creates and returns a SQLAlchemy engine
    to connect to the PostgreSQL (Supabase) database
    """

    # Fetch credentials securely from environment variables
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    # Construct database connection string
    # Format: postgresql://username:password@host:port/dbname
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

    # Create SQLAlchemy engine (connection object)
    engine = create_engine(db_url)

    return engine