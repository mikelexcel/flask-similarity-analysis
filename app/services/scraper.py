from typing import Any, Dict, List
import logging
import multiprocessing
import scrapy
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger(__name__)

_SPIDER_SETTINGS: Dict[str, Any] = {
    'LOG_ENABLED': False,           # Suppress Scrapy's version banner
    'LOG_LEVEL': 'ERROR',           # Suppress Scrapy's verbose output
    'RETRY_TIMES': 2,               # Retry failed requests twice before giving up
    'DOWNLOAD_TIMEOUT': 10,         # Abort requests that hang for more than 10 seconds
    'ROBOTSTXT_OBEY': True,         # Respect robots.txt for legality
    'USER_AGENT': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
}

class ContentSpider(scrapy.Spider):
    """Scrapes title, meta-description, and paragraph text from given URLs."""
    name = 'content_spider'
    custom_settings: Any = _SPIDER_SETTINGS

    def __init__(self, url=None, collector=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Accept single URL string or list of URLs
        if isinstance(url, str):
            self.start_urls = [url]
        elif isinstance(url, List):
            self.start_urls = url
        else:
            self.start_urls = []
    
        self.collector = collector if collector is not None else []

    def parse(self, response):
        """Extracts structured content from a single page response."""
        item = {
            'url': response.url,
            'title': response.css('title::text').get(default=''),
            'description': response.css(
                "meta[name='description']::attr(content)"
            ).get(default=''),
            'paragraphs': [
                p.strip() 
                for p in response.css('p::text').getall() 
                if p.strip()
            ]
        }
        self.collector.append(item)

def _run_spider(url, collector):
    """Runs the Scrapy crawler in a subprocess."""
    process = CrawlerProcess()
    process.crawl(ContentSpider, url=url, collector=collector)
    process.start()

class WebScraper:
    """Wraps the Scrapy spider in a subprocess to avoid Twisted reactor issues."""
    
    def __init__(self, link: str):
        self.link = link

    def scrape(self):
        """
        Spawns a subprocess, runs the spider, and returns the collected items.
        Returns an empty list if scraping fails.
        """
        manager = multiprocessing.Manager()
        collector = manager.list()

        process = multiprocessing.Process(
            target=_run_spider, 
            args=(self.link, collector,)
        )
        process.start()
        process.join()

        if process.exitcode != 0:
            logger.error("Spider subprocess exited with code %d", process.exitcode)

        return list(collector)

class LinkCredibility:
    """Combines scraping and result normalisation for a single URL."""
    _EMPTY_RESULT = [{'url': '', 'title': '', 'description': '', 'paragraphs': []}]

    def __init__(self, link):
        self.link = link
        self._scraper = WebScraper(link)

    def get_formatted_content(self):
        """
        Scrapes the link and returns a normalised list of page-data dicts.
        Falls back to _EMPTY_RESULT if no data was collected.
        """
        data = self._scraper.scrape()
        
        if not data:
            logger.warning("No content scraped from %s", self.link)
            return self._EMPTY_RESULT
            
        return data
