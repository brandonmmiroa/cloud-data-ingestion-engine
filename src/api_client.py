import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class APIClient:
    def __init__(self, base_url: str = "https://jsonplaceholder.typicode.com"):
        self.base_url = base_url

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True
    )
    def fetch_posts(self, page: int = 1, limit: int = 10) -> list[dict]:
        url = f"{self.base_url}/posts"
        params = {"_page": page, "_limit": limit}
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
