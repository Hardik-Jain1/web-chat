"""
Data fetching service for web content extraction
"""
import requests
import streamlit as st
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import time
from urllib.parse import urlparse


class DataFetcher:
    """Enhanced data fetcher with better error handling and features"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and extract content from a URL
        
        Args:
            url: URL to fetch content from
            
        Returns:
            dict: Contains text content, metadata, and status
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                st.error("Please enter a valid URL")
                return None
            
            # Show progress
            with st.spinner(f"Fetching content from {url}..."):
                start_time = time.time()
                
                # Make request
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                fetch_time = time.time() - start_time
                
                # Parse content
                content_data = self._parse_content(response, url)
                content_data['fetch_time'] = round(fetch_time, 2)
                
                st.success(f"Successfully fetched content in {fetch_time:.2f} seconds")
                return content_data
                
        except requests.exceptions.Timeout:
            st.error(f"Request timed out after {self.timeout} seconds")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the website. Please check your internet connection.")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP error {e.response.status_code}: {e.response.reason}")
            return None
        except Exception as e:
            st.error(f"Unexpected error fetching data: {str(e)}")
            return None

    def _parse_content(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract text and metadata
        
        Args:
            response: HTTP response object
            url: Original URL
            
        Returns:
            dict: Parsed content and metadata
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text content
        text_content = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract metadata
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Extract meta description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = ""
        if description_tag:
            description = description_tag.get('content', '').strip()
        
        # Extract keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = ""
        if keywords_tag:
            keywords = keywords_tag.get('content', '').strip()
        
        return {
            'text': text_content,
            'metadata': {
                'url': url,
                'title': title_text,
                'description': description,
                'keywords': keywords,
                'content_length': len(text_content),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get_url_info(self, url: str) -> Dict[str, str]:
        """
        Get basic information about a URL without fetching full content
        
        Args:
            url: URL to analyze
            
        Returns:
            dict: URL information
        """
        try:
            parsed = urlparse(url)
            return {
                'domain': parsed.netloc,
                'scheme': parsed.scheme,
                'path': parsed.path,
                'is_valid': self._is_valid_url(url)
            }
        except Exception:
            return {
                'domain': '',
                'scheme': '',
                'path': '',
                'is_valid': False
            }


# Legacy function for backward compatibility
def fetch_data(url: str) -> Optional[str]:
    """
    Legacy function to fetch data from URL (backward compatibility)
    
    Args:
        url: URL to fetch from
        
    Returns:
        str: Text content or None if failed
    """
    fetcher = DataFetcher()
    result = fetcher.fetch_data(url)
    
    if result:
        return result['text']
    return None