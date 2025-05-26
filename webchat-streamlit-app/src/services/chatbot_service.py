import streamlit as st
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from services.ai_provider import AIProviderManager, AIProviderFactory
from templates.prompt_templates import get_qa_chain_prompt


class ChatbotService:
    def __init__(self, docs, settings=None):
        """
        Initialize chatbot service with documents and settings
        
        Args:
            docs: List of processed documents
            settings: Dictionary containing provider settings
        """
        self.docs = docs
        self.settings = settings or {}
        self.ai_manager = AIProviderManager()
        self.vector_store = None
        self.qa_chain = None
        
        # Initialize vector store if docs are provided
        if docs:
            self._setup_vector_store()

    def _setup_vector_store(self):
        """Set up vector store with embeddings"""
        try:
            if not self.ai_manager.is_ready():
                raise ValueError("AI provider not ready. Please configure API key.")
            
            # Get embeddings instance
            embeddings = self.ai_manager.get_embeddings()
            
            # Create vector store
            self.vector_store = FAISS.from_documents(self.docs, embeddings)
            
            # Setup QA chain
            self._setup_qa_chain()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to setup vector store: {str(e)}")
            return False

    def _setup_qa_chain(self):
        """Set up the QA chain with current LLM"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            # Get LLM instance
            llm = self.ai_manager.get_llm()
            
            # Get prompt template
            website_name = st.session_state.get("website_name", "BotPenguin")
            prompt = get_qa_chain_prompt(website_name)
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 3}  # Return top 3 relevant documents
                ),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
        except Exception as e:
            st.error(f"Failed to setup QA chain: {str(e)}")
            raise

    def generate_response(self, query):
        """
        Generate response for user query
        
        Args:
            query: User's question/query
            
        Returns:
            dict: Response containing answer and metadata
        """
        if not query or not query.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
                "error": None
            }
        
        try:
            if not self.qa_chain:
                if not self._setup_vector_store():
                    return {
                        "answer": "Sorry, I'm not ready to answer questions yet. Please check your API key configuration.",
                        "sources": [],
                        "error": "Service not initialized"
                    }
            
            # Generate response
            result = self.qa_chain({"query": query.strip()})
            
            # Extract answer and sources
            answer = result.get("result", "I'm sorry, I couldn't generate a response.")
            source_docs = result.get("source_documents", [])
            
            # Format sources
            sources = []
            for i, doc in enumerate(source_docs[:3]):  # Limit to top 3 sources
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            st.error(error_msg)
            return {
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "sources": [],
                "error": error_msg
            }

    def is_ready(self):
        """Check if chatbot service is ready to use"""
        return (self.ai_manager.is_ready() and 
                self.docs is not None and 
                len(self.docs) > 0)

    def get_provider_info(self):
        """Get information about current AI provider"""
        provider = self.ai_manager.get_current_provider()
        providers = AIProviderFactory.get_available_providers()
        
        return {
            "provider": provider,
            "provider_name": providers.get(provider, provider),
            "is_ready": self.ai_manager.is_ready()
        }

    def update_settings(self, settings):
        """Update chatbot settings and reinitialize if needed"""
        self.settings.update(settings)
        
        # If provider settings changed, reinitialize
        if self.docs and self.ai_manager.is_ready():
            self._setup_vector_store()