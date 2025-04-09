"""
Web browser tool for accessing and interacting with web pages.
"""

import logging
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from src.tools.base_tool import BaseTool
from src.config import TOOL_TIMEOUT

logger = logging.getLogger(__name__)

class WebBrowserTool(BaseTool):
    """
    Tool for accessing and interacting with web pages.
    """
    def __init__(
        self,
        tool_id: Optional[str] = None,
        name: str = "WebBrowser",
        description: str = "Tool for accessing and interacting with web pages",
        timeout: int = TOOL_TIMEOUT
    ):
        super().__init__(
            tool_id=tool_id,
            name=name,
            description=description,
            metadata={"timeout": timeout}
        )
        self.timeout = timeout
        self.current_url = None
        self.current_page_content = None
        self.history = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the web browser tool with the provided parameters.
        
        Args:
            action: The action to perform (navigate, extract_links, extract_text, search)
            url: The URL to navigate to (for navigate action)
            query: The search query (for search action)
            selector: CSS selector for extracting specific elements
            
        Returns:
            Dictionary containing the execution results
        """
        super().execute(**kwargs)
        
        action = kwargs.get("action", "navigate")
        
        if action == "navigate":
            return self._navigate(kwargs.get("url", ""))
        elif action == "extract_links":
            return self._extract_links(kwargs.get("selector", "a"))
        elif action == "extract_text":
            return self._extract_text(kwargs.get("selector", "body"))
        elif action == "search":
            return self._search(kwargs.get("query", ""))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    def _navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Dictionary with navigation results
        """
        if not url:
            return {"status": "error", "message": "URL is required"}
        
        try:
            logger.info(f"Navigating to {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            self.current_url = url
            self.current_page_content = response.text
            
            if self.current_url not in self.history:
                self.history.append(self.current_url)
            
            # Parse the page content
            soup = BeautifulSoup(self.current_page_content, "html.parser")
            title = soup.title.string if soup.title else "No title"
            
            # Extract metadata
            meta_description = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag and "content" in meta_tag.attrs:
                meta_description = meta_tag["content"]
            
            return {
                "status": "success",
                "url": self.current_url,
                "title": title,
                "description": meta_description,
                "content_length": len(self.current_page_content),
                "content_type": response.headers.get("Content-Type", ""),
                "status_code": response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error navigating to {url}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _extract_links(self, selector: str = "a") -> Dict[str, Any]:
        """
        Extract links from the current page.
        
        Args:
            selector: CSS selector for link elements
            
        Returns:
            Dictionary with extracted links
        """
        if not self.current_page_content:
            return {"status": "error", "message": "No page loaded"}
        
        try:
            soup = BeautifulSoup(self.current_page_content, "html.parser")
            links = []
            
            for link in soup.select(selector):
                href = link.get("href")
                if href:
                    # Convert relative URLs to absolute
                    if self.current_url and not urlparse(href).netloc:
                        href = urljoin(self.current_url, href)
                    
                    links.append({
                        "url": href,
                        "text": link.get_text(strip=True),
                        "title": link.get("title", "")
                    })
            
            return {
                "status": "success",
                "links": links,
                "count": len(links)
            }
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return {"status": "error", "message": str(e)}
    
    def _extract_text(self, selector: str = "body") -> Dict[str, Any]:
        """
        Extract text from the current page.
        
        Args:
            selector: CSS selector for text elements
            
        Returns:
            Dictionary with extracted text
        """
        if not self.current_page_content:
            return {"status": "error", "message": "No page loaded"}
        
        try:
            soup = BeautifulSoup(self.current_page_content, "html.parser")
            elements = soup.select(selector)
            
            texts = [element.get_text(strip=True) for element in elements]
            combined_text = "\n\n".join(text for text in texts if text)
            
            return {
                "status": "success",
                "text": combined_text,
                "elements_count": len(elements),
                "text_length": len(combined_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {"status": "error", "message": str(e)}
    
    def _search(self, query: str) -> Dict[str, Any]:
        """
        Perform a search using a search engine.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with search results
        """
        if not query:
            return {"status": "error", "message": "Search query is required"}
        
        try:
            # Use a search engine API or scrape search results
            # For now, we'll navigate to a search URL
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            navigation_result = self._navigate(search_url)
            
            if navigation_result["status"] == "success":
                # Extract search results
                soup = BeautifulSoup(self.current_page_content, "html.parser")
                results = []
                
                # This is a simplified example and may need adjustment based on the search engine's HTML structure
                for result in soup.select("div.g"):
                    title_element = result.select_one("h3")
                    link_element = result.select_one("a")
                    snippet_element = result.select_one("div.VwiC3b")
                    
                    if title_element and link_element and "href" in link_element.attrs:
                        title = title_element.get_text(strip=True)
                        link = link_element["href"]
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet
                        })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
            else:
                return navigation_result
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the tool parameters and return values.
        
        Returns:
            Dictionary with tool schema information
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "action": {
                    "type": "string",
                    "enum": ["navigate", "extract_links", "extract_text", "search"],
                    "description": "The action to perform"
                },
                "url": {
                    "type": "string",
                    "description": "The URL to navigate to (for navigate action)"
                },
                "query": {
                    "type": "string",
                    "description": "The search query (for search action)"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for extracting specific elements"
                }
            },
            "returns": {
                "status": {
                    "type": "string",
                    "description": "Status of the operation (success or error)"
                },
                "message": {
                    "type": "string",
                    "description": "Error message if status is error"
                },
                "url": {
                    "type": "string",
                    "description": "Current URL after navigation"
                },
                "title": {
                    "type": "string",
                    "description": "Page title after navigation"
                },
                "links": {
                    "type": "array",
                    "description": "Extracted links from the page"
                },
                "text": {
                    "type": "string",
                    "description": "Extracted text from the page"
                },
                "results": {
                    "type": "array",
                    "description": "Search results"
                }
            }
        }
