"""
Document processing service for handling web content and text splitting
"""
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Optional


class DocumentProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize document processor with configurable chunking parameters
        
        Args:
            chunk_size: Size of text chunks (default from session state or 1000)
            chunk_overlap: Overlap between chunks (default from session state or 200)
        """
        self.chunk_size = chunk_size or st.session_state.get("chunk_size", 1000)
        self.chunk_overlap = chunk_overlap or st.session_state.get("chunk_overlap", 200)
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, data: str, metadata: Optional[dict] = None) -> List[Document]:
        """
        Split text data into document chunks
        
        Args:
            data: Raw text data to process
            metadata: Optional metadata to attach to documents
            
        Returns:
            List[Document]: List of processed document chunks
        """
        try:
            if not data or not data.strip():
                st.warning("No text data provided for processing")
                return []
            
            # Clean the data
            cleaned_data = self._clean_text(data)
            
            # Create document with metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "total_length": len(cleaned_data)
            })
            
            # Create initial document
            documents = [Document(page_content=cleaned_data, metadata=doc_metadata)]
            
            # Split into chunks
            split_docs = self.splitter.split_documents(documents)
            
            # Add chunk-specific metadata
            for i, doc in enumerate(split_docs):
                doc.metadata.update({
                    "chunk_id": i,
                    "chunk_count": len(split_docs)
                })
            
            st.success(f"Successfully processed {len(split_docs)} document chunks")
            return split_docs
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
            return []

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text data
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove empty lines
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text

    def get_processing_stats(self, docs: List[Document]) -> dict:
        """
        Get statistics about processed documents
        
        Args:
            docs: List of processed documents
            
        Returns:
            dict: Processing statistics
        """
        if not docs:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "chunk_size_setting": self.chunk_size,
                "chunk_overlap_setting": self.chunk_overlap
            }
        
        total_chars = sum(len(doc.page_content) for doc in docs)
        avg_chunk_size = total_chars / len(docs) if docs else 0
        
        return {
            "total_chunks": len(docs),
            "total_characters": total_chars,
            "avg_chunk_size": round(avg_chunk_size, 2),
            "chunk_size_setting": self.chunk_size,
            "chunk_overlap_setting": self.chunk_overlap
        }

    def update_settings(self, chunk_size: int, chunk_overlap: int):
        """
        Update chunking settings and recreate splitter
        
        Args:
            chunk_size: New chunk size
            chunk_overlap: New chunk overlap
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=["\n\n", "\n", " ", ""]
        )