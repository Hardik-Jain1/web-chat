"""
AI Provider Factory for handling different AI services (OpenAI, Gemini)
"""
import os
from dotenv import load_dotenv
import streamlit as st
from typing import Any, Dict
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()


class AIProviderFactory:
    """Factory class to create AI providers based on selection"""
    
    @staticmethod
    def get_api_key(provider: str, ui_api_key: str = "") -> str:
        """Get API key from UI input or environment"""
        if ui_api_key.strip():
            return ui_api_key.strip()
        
        # Fall back to environment variables
        if provider == "openai":
            return os.getenv("OPENAI_API_KEY", "")
        elif provider == "gemini":
            return os.getenv("GOOGLE_API_KEY", "")
        
        return ""
    
    @staticmethod
    def create_llm(provider: str, api_key: str = "", temperature: float = 0.3) -> Any:
        """Create a language model instance based on provider"""
        # Get actual API key
        actual_api_key = AIProviderFactory.get_api_key(provider, api_key)
        
        if not actual_api_key:
            raise ValueError(f"API key not found for {provider}. Please provide it in the UI or set environment variable.")
        
        if provider == "openai":
            return OpenAI(
                openai_api_key=actual_api_key,
                temperature=temperature
            )
        elif provider == "gemini":
            return GoogleGenerativeAI(
                google_api_key=actual_api_key,
                model="gemini-2.5-flash",
                temperature=temperature
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def create_embeddings(provider: str, api_key: str = "") -> Any:
        """Create embeddings instance based on provider"""
        # Get actual API key
        actual_api_key = AIProviderFactory.get_api_key(provider, api_key)
        
        if not actual_api_key:
            raise ValueError(f"API key not found for {provider}. Please provide it in the UI or set environment variable.")
        
        if provider == "openai":
            return OpenAIEmbeddings(openai_api_key=actual_api_key)
        elif provider == "gemini":
            print("Creating Gemini embeddings")
            return GoogleGenerativeAIEmbeddings(
                google_api_key=actual_api_key,
                model="models/embedding-001"
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_available_providers() -> Dict[str, str]:
        """Get list of available AI providers"""
        return {
            "openai": "OpenAI (GPT)",
            "gemini": "Google Gemini"
        }
    
    @staticmethod
    def validate_api_key(provider: str, api_key: str) -> bool:
        """Validate API key for the selected provider"""
        if not api_key:
            return False
        
        try:
            if provider == "openai":
                # Simple validation - try to create client
                OpenAI(openai_api_key=api_key)
                return True
            elif provider == "gemini":
                # Simple validation - try to create client
                GoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash")
                return True
        except Exception:
            return False
        
        return False


class AIProviderManager:
    """Manager class to handle AI provider state and configuration"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "provider" not in st.session_state:
            st.session_state.provider = "openai"
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        if "temperature" not in st.session_state:
            st.session_state.temperature = 0.3
        if "embeddings_ready" not in st.session_state:
            st.session_state.embeddings_ready = False
        if "llm_ready" not in st.session_state:
            st.session_state.llm_ready = False
    
    def get_current_provider(self) -> str:
        """Get currently selected provider"""
        return st.session_state.get("provider", "openai")
    
    def get_current_api_key(self) -> str:
        """Get current API key"""
        return st.session_state.get("api_key", "")
    
    def set_provider(self, provider: str):
        """Set the AI provider"""
        if provider != st.session_state.get("provider"):
            st.session_state.provider = provider
            # Reset API key when provider changes
            st.session_state.api_key = ""
            st.session_state.embeddings_ready = False
            st.session_state.llm_ready = False
    
    def set_api_key(self, api_key: str):
        """Set API key and validate"""
        st.session_state.api_key = api_key
        provider = self.get_current_provider()
        
        if AIProviderFactory.validate_api_key(provider, api_key):
            st.session_state.embeddings_ready = True
            st.session_state.llm_ready = True
        else:
            st.session_state.embeddings_ready = False
            st.session_state.llm_ready = False
    
    def is_ready(self) -> bool:
        """Check if AI provider is ready to use"""
        return (st.session_state.get("embeddings_ready", False) and 
                st.session_state.get("llm_ready", False))
    
    def get_llm(self) -> Any:
        """Get configured LLM instance"""
        provider = self.get_current_provider()
        api_key = self.get_current_api_key()
        temperature = st.session_state.get("temperature", 0.3)
        
        return AIProviderFactory.create_llm(provider, api_key, temperature)
    
    def get_embeddings(self) -> Any:
        """Get configured embeddings instance"""
        provider = self.get_current_provider()
        api_key = self.get_current_api_key()
        
        return AIProviderFactory.create_embeddings(provider, api_key)
