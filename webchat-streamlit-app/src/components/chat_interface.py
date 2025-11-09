"""
Chat interface component for the WebChat application
"""
import os
from dotenv import load_dotenv
import streamlit as st
from typing import Optional, Dict, Any
import time

# Load environment variables
load_dotenv()


class ChatInterface:
    def __init__(self, chatbot_service=None):
        """
        Initialize chat interface
        
        Args:
            chatbot_service: ChatbotService instance
        """
        self.chatbot_service = chatbot_service
        self._initialize_chat_history()

    def _initialize_chat_history(self):
        """Initialize chat history in session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def display(self):
        """Display the complete chat interface"""
        if not self.chatbot_service or not self.chatbot_service.is_ready():
            self._display_not_ready_message()
            return

        st.subheader("💬 Chat with your Website")
        
        # Display provider info
        self._display_provider_info()
        
        # Chat history
        self._display_chat_history()
        
        # Chat input
        self._display_chat_input()

    def _display_not_ready_message(self):
        """Display message when chatbot is not ready"""
        st.warning("🔧 Please configure your AI provider and fetch website data first!")
        
        with st.expander("Setup Instructions", expanded=True):
            st.markdown("""
            **To start chatting:**
            1. ⚙️ Configure your AI provider in the sidebar
            2. 🔑 Enter your API key
            3. 🌐 Enter a website URL and click "Fetch Data"
            4. 💬 Start chatting!
            """)

    def _display_provider_info(self):
        """Display current AI provider information"""
        if self.chatbot_service:
            provider_info = self.chatbot_service.get_provider_info()
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.caption(f"🤖 Provider: **{provider_info['provider_name']}**")
            with col2:
                status = "🟢 Ready" if provider_info['is_ready'] else "🔴 Not Ready"
                st.caption(f"Status: {status}")
            with col3:
                if st.button("🗑️", help="Clear chat history"):
                    st.session_state.messages = []
                    st.rerun()

    def _display_chat_history(self):
        """Display chat message history"""
        # Create a container for chat messages with scrolling
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        st.markdown(message["content"])
                    else:
                        # Display assistant response
                        st.markdown(message["content"])
                        
                        # Show sources if available
                        if "sources" in message and message["sources"]:
                            with st.expander("📚 Sources", expanded=False):
                                for j, source in enumerate(message["sources"]):
                                    st.markdown(f"**Source {j+1}:**")
                                    st.text(source["content"])
                                    if source.get("metadata"):
                                        st.caption(f"Metadata: {source['metadata']}")

    def _display_chat_input(self):
        """Display chat input and handle user messages"""
        # Chat input
        if prompt := st.chat_input("Ask a question about the website..."):
            self._handle_user_message(prompt)

    def _handle_user_message(self, user_input: str):
        """
        Handle user message and generate response
        
        Args:
            user_input: User's message
        """
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": time.time()
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = self.chatbot_service.generate_response(user_input)
            
            # Display the response
            st.markdown(response_data["answer"])
            
            # Display sources if available
            if response_data.get("sources"):
                with st.expander("📚 Sources", expanded=False):
                    for i, source in enumerate(response_data["sources"]):
                        st.markdown(f"**Source {i+1}:**")
                        st.text(source["content"])
                        if source.get("metadata"):
                            st.caption(f"Metadata: {source['metadata']}")

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data["answer"],
            "sources": response_data.get("sources", []),
            "timestamp": time.time(),
            "error": response_data.get("error")
        })

    def display_simple(self):
        """Display a simplified chat interface for testing"""
        st.subheader("💬 Simple Chat")
        
        user_input = st.text_input("Ask your question:", key="simple_chat_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_clicked = st.button("Send", type="primary")
        with col2:
            if st.button("Clear"):
                st.session_state.messages = []
                st.rerun()
        
        if submit_clicked and user_input:
            if not self.chatbot_service or not self.chatbot_service.is_ready():
                st.error("Chatbot service is not ready. Please check your configuration.")
                return
            
            # Show thinking spinner and generate response
            with st.spinner("Generating response..."):
                response_data = self.chatbot_service.generate_response(user_input)
            
            # Display response
            st.subheader("Response:")
            st.write(response_data["answer"])
            
            # Display sources
            if response_data.get("sources"):
                with st.expander("View Sources"):
                    for i, source in enumerate(response_data["sources"]):
                        st.markdown(f"**Source {i+1}:**")
                        st.text(source["content"][:200] + "..." if len(source["content"]) > 200 else source["content"])

    def get_chat_stats(self) -> Dict[str, Any]:
        """Get statistics about the current chat session"""
        messages = st.session_state.get("messages", [])
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "avg_response_time": self._calculate_avg_response_time(messages)
        }

    def _calculate_avg_response_time(self, messages) -> float:
        """Calculate average response time"""
        response_times = []
        for i in range(1, len(messages)):
            if (messages[i-1]["role"] == "user" and 
                messages[i]["role"] == "assistant"):
                time_diff = messages[i]["timestamp"] - messages[i-1]["timestamp"]
                response_times.append(time_diff)
        
        return sum(response_times) / len(response_times) if response_times else 0