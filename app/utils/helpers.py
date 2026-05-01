from typing import Dict, List
import logging
from app.services.scraper import LinkCredibility
from app.services import analyser
import numpy as np

logger = logging.getLogger(__name__)

def scrape_link(link: str) -> Dict | None:
    """
    Scrapes a single URL and returns its content dict, or None if it should
    be skipped.
    Filters out non-HTTP URLs and video platforms that don't contain 
    comparable article content.
    """
    _SKIP_DOMAINS = {'youtube.com', 'youtu.be', 'vimeo.com', 'tiktok.com'}

    if not isinstance(link, str) or not link.startswith('http'):
        return None

    if any(domain in link for domain in _SKIP_DOMAINS):
        return None

    try:
        data = LinkCredibility(link).get_formatted_content()
        if data and data[0].get('title'):
            return data[0]
        
    except Exception as e:
        logger.warning("Failed to scrape comparison link %s: %s", link, e)

    return None

def compute_scores(user_info: Dict, comparison_items: List[Dict]) -> Dict:
    """
    Calculates TF-IDF cosine similarity scores between the user's page and
    each comparison page across three fields: title, description, and content.
    Content is derived by joining each page's paragraph list into a single
    string.
    Returns a dict of per-field mean scores and a weighted overall score.
    """
    title_scores, desc_scores, content_scores = [], [], []

    # Join paragraphs into one string to be compared as document
    user_content = ' '.join(user_info.get('paragraphs', []))

    for item in comparison_items:
        item_content = ' '.join(item.get('paragraphs', []))

        title_score = analyser.calculate_similarity(
            user_info.get('title', ''), item.get('title', ''))
        desc_score = analyser.calculate_similarity(
            user_info.get('description', ''), item.get('description', ''))
        content_score = analyser.calculate_similarity(
            user_content, item_content)

        if 0.0 <= title_score <= 1.0: title_scores.append(title_score)
        if 0.0 <= desc_score <= 1.0: desc_scores.append(desc_score)
        if 0.0 <= content_score <= 1.0: content_scores.append(content_score)

    overall = analyser.get_final_score(title_scores, desc_scores, content_scores)

    return {
        'title_score': round(float(np.mean(title_scores)) if title_scores else 0.0, 4),
        'description_score': round(float(np.mean(desc_scores)) if desc_scores else 0.0, 4),
        'content_score': round(float(np.mean(content_scores)) if content_scores else 0.0, 4),
        'overall_score': round(overall, 4),
        'sources_compared': len(comparison_items),
    }