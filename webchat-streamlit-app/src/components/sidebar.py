import streamlit as st
from services.ai_provider import AIProviderFactory, AIProviderManager


class Sidebar:
    def __init__(self, config=None):
        self.config = config or {}
        self.ai_manager = AIProviderManager()

    def display(self):
        """Display the sidebar with AI provider selection and settings"""
        st.sidebar.title("🤖 WebChat Settings")
        
        # AI Provider Selection
        self._display_ai_provider_section()
        
        # Advanced Settings
        self._display_advanced_settings()
        
        # Chat Settings
        self._display_chat_settings()
        
        # Status indicator
        self._display_status()
        
        return self._get_current_settings()

    def _display_ai_provider_section(self):
        """Display AI provider selection and API key input"""
        st.sidebar.subheader("🔧 AI Provider")
        
        # Provider selection
        providers = AIProviderFactory.get_available_providers()
        current_provider = self.ai_manager.get_current_provider()
        
        selected_provider = st.sidebar.selectbox(
            "Select AI Provider",
            options=list(providers.keys()),
            format_func=lambda x: providers[x],
            index=list(providers.keys()).index(current_provider) if current_provider in providers else 0,
            help="Choose between OpenAI GPT or Google Gemini"
        )
        
        # Update provider if changed
        if selected_provider != current_provider:
            self.ai_manager.set_provider(selected_provider)
            st.rerun()
        
        # API Key input
        api_key_label = "OpenAI API Key" if selected_provider == "openai" else "Google API Key"
        api_key_help = (
            "Enter your OpenAI API key" if selected_provider == "openai" 
            else "Enter your Google API key for Gemini"
        )
        
        current_api_key = self.ai_manager.get_current_api_key()
        api_key = st.sidebar.text_input(
            api_key_label,
            value=current_api_key,
            type="password",
            help=api_key_help
        )
        
        # Update API key if changed
        if api_key != current_api_key:
            self.ai_manager.set_api_key(api_key)
            if api_key:  # Only rerun if API key is provided
                st.rerun()

    def _display_advanced_settings(self):
        """Display advanced AI settings"""
        with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
            # Temperature setting
            temperature = st.slider(
                "Response Creativity",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("temperature", 0.3),
                step=0.1,
                help="Higher values make responses more creative but less focused"
            )
            st.session_state.temperature = temperature
            
            # Document processing settings
            st.subheader("Document Processing")
            chunk_size = st.number_input(
                "Chunk Size",
                min_value=500,
                max_value=2000,
                value=st.session_state.get("chunk_size", 1000),
                step=100,
                help="Size of text chunks for processing"
            )
            st.session_state.chunk_size = chunk_size
            
            chunk_overlap = st.number_input(
                "Chunk Overlap",
                min_value=50,
                max_value=500,
                value=st.session_state.get("chunk_overlap", 200),
                step=50,
                help="Overlap between text chunks"
            )
            st.session_state.chunk_overlap = chunk_overlap

    def _display_chat_settings(self):
        """Display chat-specific settings"""
        with st.sidebar.expander("💬 Chat Settings", expanded=False):
            website_name = st.text_input(
                "Website/Brand Name",
                value=st.session_state.get("website_name", "BotPenguin"),
                help="Name of the website/brand for the chatbot persona"
            )
            st.session_state.website_name = website_name
            
            # Clear chat history button
            if st.button("🗑️ Clear Chat History", help="Clear all chat messages"):
                if "messages" in st.session_state:
                    st.session_state.messages = []
                st.success("Chat history cleared!")

    def _display_status(self):
        """Display current AI provider status"""
        st.sidebar.subheader("📊 Status")
        
        provider = self.ai_manager.get_current_provider()
        providers = AIProviderFactory.get_available_providers()
        
        st.sidebar.write(f"**Provider:** {providers.get(provider, provider)}")
        
        if self.ai_manager.is_ready():
            st.sidebar.success("✅ Ready to chat!")
        else:
            st.sidebar.warning("⚠️ Please enter a valid API key")
            
        # Show API key status
        api_key = self.ai_manager.get_current_api_key()
        if api_key:
            st.sidebar.write(f"**API Key:** {'*' * min(len(api_key), 8)}...")
        else:
            st.sidebar.write("**API Key:** Not provided")

    def _get_current_settings(self):
        """Get current sidebar settings"""
        return {
            "provider": self.ai_manager.get_current_provider(),
            "api_key": self.ai_manager.get_current_api_key(),
            "temperature": st.session_state.get("temperature", 0.3),
            "chunk_size": st.session_state.get("chunk_size", 1000),
            "chunk_overlap": st.session_state.get("chunk_overlap", 200),
            "website_name": st.session_state.get("website_name", "BotPenguin"),
            "is_ready": self.ai_manager.is_ready()
        }