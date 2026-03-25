import requests
from typing import Dict, List, Optional, Any

class VAClient:
    """V&A Collections API Client (V2)"""
    
    BASE_URL = "https://api.vam.ac.uk/v2"
    
    def __init__(self):
        self.session = requests.Session()

    def search(self, query: str, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """Search the collection."""
        params = {
            "q": query,
            "page": page,
            "page_size": page_size,
            "images_exist": 1 # For a visual interface, images are essential
        }
        url = f"{self.BASE_URL}/objects/search"
        print(f"DEBUG: API Search URL: {url} with params: {params}")
        response = self.session.get(url, params=params)
        print(f"DEBUG: API Response Status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"DEBUG: API Records Found: {data.get('info', {}).get('record_count', 0)}")
        return data

    def get_clusters(self, query: str, cluster_field: str) -> Dict[str, Any]:
        """Get summary clusters for a specific field based on a search."""
        params = {
            "q": query
        }
        # Correct endpoint according to research: /objects/clusters/{field}/search
        url = f"{self.BASE_URL}/objects/clusters/{cluster_field}/search"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_object(self, object_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a single item."""
        url = f"{self.BASE_URL}/museumobject/{object_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_featured_items(self, page_size: int = 50) -> Dict[str, Any]:
        """Get high-quality items for the 'Show First' experience."""
        # Search for something broad that often has high-quality images
        return self.search(query="", page=1, page_size=page_size)

    def get_objects_bulk(self, system_numbers: List[str]) -> List[Dict[str, Any]]:
        """Fetch multiple objects in parallel to get full metadata."""
        from concurrent.futures import ThreadPoolExecutor
        
        def fetch_one(sid):
            try:
                return self.get_object(sid).get("record", {})
            except:
                return {}

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_one, system_numbers))
        return results

if __name__ == "__main__":
    # Quick sanity check
    client = VAClient()
    try:
        results = client.search("chair", page_size=10)
        print(f"Search found: {results['info']['record_count']} items.")
        if results.get('records'):
            print("First 5 objectTypes:")
            for r in results['records'][:5]:
                print(f" - {r.get('objectType')}")
        
        clusters = client.get_clusters("chair", "category")
        print(f"Top 5 Category clusters:")
        for c in clusters[:5]:
            print(f" - {c['value']} ({c['count']})")
    except Exception as e:
        print(f"Error: {e}")
