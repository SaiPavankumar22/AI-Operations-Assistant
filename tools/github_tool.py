import os
import requests
from typing import Dict, List, Any, Optional


class GitHubTool:

    def __init__(self):
        self.api_key = os.environ.get("GITHUB_API_KEY")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"token {self.api_key}"
    
    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        limit: int = 5
    ) -> List[Dict[str, Any]]:

        try:
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            repos = []
            
            for item in data.get("items", []):
                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language"),
                    "url": item.get("html_url"),
                    "topics": item.get("topics", [])
                })
            
            return repos
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"GitHub API request failed: {str(e)}"}]
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:

        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "watchers": data.get("watchers_count"),
                "language": data.get("language"),
                "url": data.get("html_url"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "open_issues": data.get("open_issues_count"),
                "topics": data.get("topics", [])
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"GitHub API request failed: {str(e)}"}
    
    def get_user_repos(self, username: str, limit: int = 5) -> List[Dict[str, Any]]:

        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {
                "sort": "updated",
                "per_page": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            repos = []
            for item in response.json():
                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language"),
                    "url": item.get("html_url")
                })
            
            return repos
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"GitHub API request failed: {str(e)}"}]