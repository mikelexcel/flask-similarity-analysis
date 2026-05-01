from typing import Any, List
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Computes the TF-IDF cosine similarity between two strings.
    Returns a float in [0.0, 1.0] where 1.0 means identical content.
    Returns 0.0 safely if either input is empty or an error occurs.
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        docs = [text1, text2]
        tfidf_matrix: Any = TfidfVectorizer().fit_transform(docs)
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(score[0][0])
    
    except ValueError as e:
        logger.warning("Similarity calculation failed: %s", e)
        return 0.0

def get_final_score(
        title_scores: List[float], 
        desc_scores: List[float], 
        content_scores: List[float]
    ) -> float:
    """
    Combines per-field similarity scores into a single accuracy score.
    Average each field's scores to get one representative value per field, then
    take the median across the three field averages to reduce the impact of 
    any one field being an outlier (e.g. a missing description).
    Returns a float in [0.0, 1.0].
    """

    title_mean = float(np.mean(title_scores)) if title_scores else 0.0
    desc_mean = float(np.mean(desc_scores)) if desc_scores else 0.0
    content_mean = float(np.mean(content_scores)) if content_scores else 0.0

    overall = float(np.median([title_mean, desc_mean, content_mean]))

    return 0.0 if np.isnan(overall) else overall