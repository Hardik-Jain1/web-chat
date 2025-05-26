"""
Main WebChat Streamlit Application with AI Provider Selection
"""
import streamlit as st
import os
from components.chat_interface import ChatInterface
from components.sidebar import Sidebar
from services.data_fetcher import DataFetcher
from services.document_processor import DocumentProcessor
from services.chatbot_service import ChatbotService
from services.ai_provider import AIProviderManager
from utils.config import load_config, get_session_config


def initialize_app():
    """Initialize the Streamlit app configuration"""
    st.set_page_config(
        page_title="WebChat AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        "documents_processed": False,
        "current_url": "",
        "processing_stats": {},
        "chatbot_ready": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    """Main application function"""
    initialize_app()
    initialize_session_state()
    
    # Load configuration
    config = load_config()
    
    # Initialize AI Provider Manager
    ai_manager = AIProviderManager()
    
    # Main title
    st.title("🤖 WebChat AI Assistant")
    st.markdown("*Chat with any website using OpenAI or Google Gemini*")
    
    # Sidebar for settings
    sidebar = Sidebar(config)
    settings = sidebar.display()
    
    # Main content area
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("📥 Website Data Input")
        display_data_input_section(settings)
    
    with col2:
        st.subheader("💬 Chat Interface")
        display_chat_section(settings)
    
    # Footer with stats
    display_footer_stats()

def display_data_input_section(settings):
    """Display the data input and processing section"""
    
    # URL input
    url = st.text_input(
        "Enter Website URL:",
        value=st.session_state.get("current_url", ""),
        placeholder="https://example.com",
        help="Enter the URL of the website you want to chat with"
    )
    
    # Fetch data button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fetch_clicked = st.button(
            "🌐 Fetch Data", 
            type="primary",
            disabled=not url or not settings.get("is_ready", False),
            help="Fetch and process website content"
        )
    
    with col2:
        if st.button("🔄 Reset", help="Clear all data and start fresh"):
            reset_application_state()
            st.rerun()
    
    # Display URL info
    if url:
        display_url_info(url)
    
    # Handle data fetching
    if fetch_clicked and url and settings.get("is_ready", False):
        handle_data_fetching(url, settings)
    
    # Display processing status
    display_processing_status()

def display_url_info(url):
    """Display information about the entered URL"""
    fetcher = DataFetcher()
    url_info = fetcher.get_url_info(url)
    
    if url_info["is_valid"]:
        st.success(f"✅ Valid URL: {url_info['domain']}")
    else:
        st.error("❌ Invalid URL format")

def handle_data_fetching(url, settings):
    """Handle the data fetching and processing workflow"""
    try:
        # Update current URL
        st.session_state.current_url = url
        
        # Fetch data
        fetcher = DataFetcher()
        
        with st.status("Fetching website data...", expanded=True) as status:
            st.write("🌐 Connecting to website...")
            data_result = fetcher.fetch_data(url)
            
            if not data_result:
                st.error("Failed to fetch website data")
                return
            
            st.write("📄 Processing content...")
            
            # Process documents
            processor = DocumentProcessor(
                chunk_size=settings.get("chunk_size", 1000),
                chunk_overlap=settings.get("chunk_overlap", 200)
            )
            
            docs = processor.split_documents(
                data_result["text"], 
                metadata=data_result["metadata"]
            )
            
            if not docs:
                st.error("No content could be extracted from the website")
                return
            
            # Store processing stats
            st.session_state.processing_stats = processor.get_processing_stats(docs)
            
            st.write("🤖 Initializing AI chatbot...")
            
            # Initialize chatbot
            chatbot = ChatbotService(docs, settings)
            
            # Store in session state
            st.session_state.chatbot_service = chatbot
            st.session_state.documents_processed = True
            st.session_state.chatbot_ready = chatbot.is_ready()
            
            status.update(label="✅ Website data processed successfully!", state="complete")
        
        st.success(f"Successfully processed {len(docs)} document chunks!")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error processing website data: {str(e)}")

def display_processing_status():
    """Display current processing status and statistics"""
    if st.session_state.get("documents_processed", False):
        with st.expander("📊 Processing Statistics", expanded=False):
            stats = st.session_state.get("processing_stats", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Chunks", stats.get("total_chunks", 0))
                st.metric("Chunk Size Setting", stats.get("chunk_size_setting", 0))
            
            with col2:
                st.metric("Total Characters", stats.get("total_characters", 0))
                st.metric("Avg Chunk Size", stats.get("avg_chunk_size", 0))

def display_chat_section(settings):
    """Display the chat interface section"""
    
    if not settings.get("is_ready", False):
        st.warning("⚠️ Please configure your AI provider in the sidebar first")
        return
    
    if not st.session_state.get("documents_processed", False):
        st.info("📝 Please fetch website data first to start chatting")
        return
    
    # Get chatbot service from session state
    chatbot_service = st.session_state.get("chatbot_service")
    
    if chatbot_service and chatbot_service.is_ready():
        # Display chat interface
        chat_interface = ChatInterface(chatbot_service)
        chat_interface.display()
    else:
        st.error("❌ Chatbot service is not ready")

def display_footer_stats():
    """Display footer with application statistics"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅ Ready" if st.session_state.get("chatbot_ready", False) else "⏳ Waiting"
        st.metric("Chatbot Status", status)
    
    with col2:
        url = st.session_state.get("current_url", "None")
        domain = url.split("//")[-1].split("/")[0] if url != "None" else "None"
        st.metric("Current Website", domain)
    
    with col3:
        chunks = st.session_state.get("processing_stats", {}).get("total_chunks", 0)
        st.metric("Document Chunks", chunks)
    
    with col4:
        messages = len(st.session_state.get("messages", []))
        st.metric("Chat Messages", messages)

def reset_application_state():
    """Reset application state for fresh start"""
    keys_to_reset = [
        "documents_processed",
        "current_url", 
        "processing_stats",
        "chatbot_ready",
        "chatbot_service",
        "messages"
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

if __name__ == "__main__":
    main()