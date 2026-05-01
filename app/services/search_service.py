from typing import List
import logging
import requests
import serpapi
from duckduckgo_search import DDGS
from config import Config

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5

def get_similar_links(query):
    """
    Returns up to _MAX_RESULTS URLs relevant to query.

    Search backend priority, from highest to lowest, is Google Custom Search 
    (requires SEARCH_ENGINE_ID + GENAI_API_KEY), then SerpApi Google Search 
    (requires SERPAPI_API_KEY), then DuckDuckGo (no key required, 
    always available as final fallback)
    """
    if not query or not query.strip():
        logger.warning("Empty query passed to get_similar_links")
        return []
    
    if Config.SEARCH_ENGINE_ID and Config.GENAI_API_KEY:
        links = _google_cse_search(query)
        if links:
            return links
        
    if Config.SERPAPI_API_KEY:
        links = _serpapi_search(query)
        if links:
            return links
        
    return _duckduckgo_search(query)


def _google_cse_search(query: str) -> List[str]:
    """Queries the Google Custom Search JSON API."""
    try:
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params={
                'q': query,
                'key': Config.GENAI_API_KEY,
                'cx': Config.SEARCH_ENGINE_ID,
                'num': _MAX_RESULTS,
            },
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get('items', [])
        links = [item['link'] for item in items if 'link' in item]
        logger.debug("Google CSE returned %d links", len(links))
        return links

    except requests.RequestException as e:
        logger.warning("Google CSE request failed: %s", e)
        return []
    
def _serpapi_search(query: str) -> List[str]:
    """Queries Google via SerpApi."""
    try:
        result = serpapi.GoogleSearch({
            'q': query,
            'api_key': Config.SERPAPI_API_KEY,
            'num': _MAX_RESULTS,
        }).get_dict()

        links = [
            res['link']
            for res in result.get('organic_results', [])
            if 'link' in res
        ]
        logger.debug("SerpApi returned %d links", len(links))
        return links

    except Exception as e:
        logger.warning("SerpApi request failed: %s", e)
        return []
    
def _duckduckgo_search(query: str) -> List[str]:
    """Queries DuckDuckGo (no API key required)."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=_MAX_RESULTS))
        links = [result['href'] for result in results if 'href' in result]
        logger.debug("DuckDuckGo returned %d links", len(links))
        return links

    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return []