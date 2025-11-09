import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration including API keys and provider settings"""
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
        "DEFAULT_PROVIDER": os.getenv("DEFAULT_PROVIDER", "openai"),
        "DEFAULT_TEMPERATURE": float(os.getenv("DEFAULT_TEMPERATURE", "0.3")),
        "DEFAULT_CHUNK_SIZE": int(os.getenv("DEFAULT_CHUNK_SIZE", "1000")),
        "DEFAULT_CHUNK_OVERLAP": int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))
    }

def get_session_config():
    """Get configuration from Streamlit session state"""
    return {
        "provider": st.session_state.get("provider", "openai"),
        "api_key": st.session_state.get("api_key", ""),
        "temperature": st.session_state.get("temperature", 0.3),
        "chunk_size": st.session_state.get("chunk_size", 1000),
        "chunk_overlap": st.session_state.get("chunk_overlap", 200),
        "website_name": st.session_state.get("website_name", "BotPenguin")
    }