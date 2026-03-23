import sys
import os

# Add project root to Python path
# This allows us to import modules from config/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from config.db import get_engine

# Set page title in browser tab
st.set_page_config(page_title="Chinook Dashboard", layout="wide")

# Main title of the app
st.title("Chinook Dashboard - Test Connection")

# Get database engine from db.py
engine = get_engine()

# Try connecting to database
try:
    # Open connection
    with engine.connect() as conn:
        # If successful, show success message
        st.success("✅ Connected to database successfully!")

except Exception as e:
    # If connection fails, show error message
    st.error(f"❌ Connection failed: {e}")