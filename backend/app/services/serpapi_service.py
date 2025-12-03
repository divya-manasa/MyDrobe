import requests
from app.config import get_settings

settings = get_settings()

class SerpAPIService:
    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
    
    def search_products(self, query: str, location: str = "United States", num_results: int = 10) -> list:
        """Search for products using Google Shopping"""
        if not self.api_key:
            return []
        
        params = {
            "engine": "google_shopping",
            "q": query,
            "location": location,
            "api_key": self.api_key,
            "num": num_results
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("shopping_results", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "price": item.get("price", "N/A"),
                        "source": item.get("source", ""),
                        "link": item.get("link", ""),
                        "thumbnail": item.get("thumbnail", ""),
                        "rating": item.get("rating", 0),
                        "reviews": item.get("reviews", 0)
                    })
                
                return results
            return []
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return []
    
    def search_fashion_trends(self, query: str, location: str = "United States") -> list:
        """Search for fashion trends"""
        if not self.api_key:
            return []
        
        params = {
            "engine": "google",
            "q": f"{query} fashion trends",
            "location": location,
            "api_key": self.api_key,
            "num": 5
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("organic_results", [])[:5]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })
                
                return results
            return []
        except Exception as e:
            print(f"SerpAPI trends error: {e}")
            return []

serpapi_service = SerpAPIService()
