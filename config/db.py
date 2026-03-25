from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------
# This loads variables from a .env file (for local development)
# In Streamlit Cloud, values will come from "Secrets"
load_dotenv()

def get_engine():
    """
    Creates and returns a SQLAlchemy engine to connect
    to the PostgreSQL (Supabase) database.
    """
    # --------------------------------------------------
    # FETCH DATABASE CREDENTIALS FROM ENV VARIABLES
    # --------------------------------------------------
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")

    # --------------------------------------------------
    # VALIDATION CHECK
    # --------------------------------------------------
    # If any variable is missing, raise a clear error
    if not all([user, password, host, port, dbname]):
        raise ValueError(
            "Missing database credentials. "
            "Please check your .env file or Streamlit secrets configuration."
        )

    # --------------------------------------------------
    # CREATE DATABASE CONNECTION STRING
    # --------------------------------------------------
    # Format:
    # postgresql+psycopg2://username:password@host:port/dbname
    # sslmode=require is needed for secure Supabase connection
    db_url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{dbname}?sslmode=require"
    )

    # --------------------------------------------------
    # CREATE AND RETURN ENGINE
    # --------------------------------------------------
    engine = create_engine(db_url)

    return engine