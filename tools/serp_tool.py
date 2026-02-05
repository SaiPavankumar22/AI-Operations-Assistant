import os
import requests
from typing import Dict, List, Any, Optional


class SerpTool:
    """Tool for interacting with SERP API (Google Search)"""
    
    def __init__(self):
        self.api_key = os.environ.get("SERP_API_KEY")
        self.base_url = "https://serpapi.com/search"
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        location: Optional[str] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": num_results,
                "hl": language,
                "engine": "google"
            }
            
            if location:
                params["location"] = location
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("organic_results", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "displayed_link": item.get("displayed_link"),
                    "position": item.get("position")
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"SERP API request failed: {str(e)}"}]
    
    def search_news(
        self,
        query: str,
        num_results: int = 5,
        time_period: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": num_results,
                "engine": "google",
                "tbm": "nws"  # News search
            }
            
            if time_period:
                params["tbs"] = f"qdr:{time_period}"
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("news_results", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "source": item.get("source"),
                    "date": item.get("date"),
                    "thumbnail": item.get("thumbnail")
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"SERP API request failed: {str(e)}"}]
    
    def search_images(
        self,
        query: str,
        num_results: int = 5,
        image_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "num": num_results,
                "engine": "google",
                "tbm": "isch"  # Image search
            }
            
            if image_type:
                params["tbs"] = f"itp:{image_type}"
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("images_results", []):
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "source": item.get("source"),
                    "thumbnail": item.get("thumbnail"),
                    "original": item.get("original"),
                    "position": item.get("position")
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"SERP API request failed: {str(e)}"}]
    
    def get_answer_box(self, query: str) -> Optional[Dict[str, Any]]:

        try:
            params = {
                "api_key": self.api_key,
                "q": query,
                "engine": "google"
            }
            
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for answer box
            answer_box = data.get("answer_box")
            if answer_box:
                return {
                    "answer": answer_box.get("answer") or answer_box.get("snippet"),
                    "title": answer_box.get("title"),
                    "link": answer_box.get("link"),
                    "type": answer_box.get("type")
                }
            
            # Check for knowledge graph
            knowledge_graph = data.get("knowledge_graph")
            if knowledge_graph:
                return {
                    "answer": knowledge_graph.get("description"),
                    "title": knowledge_graph.get("title"),
                    "type": "knowledge_graph"
                }
            
            return None
        
        except requests.exceptions.RequestException as e:
            return {"error": f"SERP API request failed: {str(e)}"}