import logging
from flask import Blueprint, request, jsonify, current_app
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.scraper import LinkCredibility
from app.services.search_service import get_similar_links
from app.utils.helpers import scrape_link, compute_scores

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

_MAX_COMPARISON_SITES = 5
_SCRAPE_WORKERS = 4

@main_bp.route('/analyse', methods=['POST'])
def analyse():
    """
    Main analysis endpoint.
    Expects JSON body and returns similarity scores comparing the page against 
    search results for the same topic, giving a rough signal of how consistent its
    content is with what other sources say.
    Scrape the submitted URL, search for similar pages using the page title as 
    the query, scrape comparison pages in parallel (up to _SCRAPE_WORKERS threads), 
    score each field with TF-IDF cosine similarity and return per-field and overall scores.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400
    
    user_link = data.get('url', '').strip()
    if not user_link:
        return jsonify({'error': 'Missing required field: url'}), 400

    if not user_link.startswith('http'):
        return jsonify({'error': 'URL must begin with http:// or https://'}), 400

    try:
        # Scrape submitted URL
        user_data = LinkCredibility(user_link).get_formatted_content()
        user_info = user_data[0]

        title = user_info.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Could not extract a title from the provided URL'}), 422
        
        logger.debug("Scraped user page - title: %s", title)

        # Find similar pages to compare against
        similar_links = get_similar_links(title)

        if not similar_links:
            logger.warning("No comparison links found for query: %s", title)
            return jsonify({'error': 'No comparison sources found for this page'}), 422

        # Exclude submitted URL from comparison links
        comparison_links = [
            link for link in similar_links
            if link != user_link
        ][:_MAX_COMPARISON_SITES]

        # Scrape comparison pages in parallel
        comparison_items = []
        with ThreadPoolExecutor(max_workers=_SCRAPE_WORKERS) as executor:
            futures = {
                executor.submit(scrape_link, link): link
                for link in comparison_links
            }
            for future in as_completed(futures):
                result = future.result()
                if result:
                    comparison_items.append(result)

        if not comparison_items:
            return jsonify({'error': 'Could not scrape any comparison sources'}), 422

        # Score and return
        scores = compute_scores(user_info, comparison_items)
        logger.info(
            "Analysis complete for %s - overall: %.4f (%d sources)",
            user_link, scores['overall_score'], scores['sources_compared']
        )
        return jsonify(scores), 200

    except Exception as e:
        current_app.logger.error("Analysis failed for %s: %s", user_link, e, exc_info=True)
        return jsonify({'error': 'An internal error occurred during analysis'}), 500    