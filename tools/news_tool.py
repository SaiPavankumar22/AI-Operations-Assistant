import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class NewsTool:
    """Tool for interacting with News API"""
    
    def __init__(self):
        self.api_key = os.environ.get("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
  
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "pageSize": limit
            }
            
            if country:
                params["country"] = country
            if category:
                params["category"] = category
            if query:
                params["q"] = query
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "author": article.get("author"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "content": article.get("content")
                })
            
            return articles
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"News API request failed: {str(e)}"}]
    
    def search_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "relevancy",
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        try:
            url = f"{self.base_url}/everything"
            
            # Default date range: last 7 days
            if not from_date:
                from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                "apiKey": self.api_key,
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": language,
                "sortBy": sort_by,
                "pageSize": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "author": article.get("author"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "content": article.get("content")
                })
            
            return articles
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"News API request failed: {str(e)}"}]
    
    def get_sources(self, category: Optional[str] = None, language: str = "en") -> List[Dict[str, Any]]:

        try:
            url = f"{self.base_url}/sources"
            params = {
                "apiKey": self.api_key,
                "language": language
            }
            
            if category:
                params["category"] = category
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            sources = []
            for source in data.get("sources", []):
                sources.append({
                    "id": source.get("id"),
                    "name": source.get("name"),
                    "description": source.get("description"),
                    "url": source.get("url"),
                    "category": source.get("category"),
                    "country": source.get("country")
                })
            
            return sources
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"News API request failed: {str(e)}"}]