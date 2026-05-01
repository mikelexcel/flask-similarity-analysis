# Similarity Analysis Flask API

This repository contains a high-performance **Flask-based API** designed to perform content similarity and consistency analysis. The application scrapes a target URL, identifies related content across the web using various search engines, and computes similarity scores using **TF-IDF (Term Frequency-Inverse Document Frequency) cosine similarity**. This serves as a "credibility signal" by measuring how closely a page's content aligns with the broader web consensus on the same topic.

---

## 🚀 Key Features

*   **Multimodal Scraper**: Uses `Scrapy` to extract titles, meta-descriptions, and paragraph content. To handle the Twisted reactor limitations of Scrapy within Flask, each scrape is executed in a dedicated subprocess.
*   **Parallel Processing**: Utilises `ThreadPoolExecutor` to scrape multiple comparison sites concurrently, significantly reducing response latency.
*   **Dynamic Search Backend**: A tiered fallback system for finding comparison links:
    1.  **Google Custom Search API** (Primary)
    2.  **SerpApi** (Secondary)
    3.  **DuckDuckGo** (Tertiary/No-key fallback)
*   **NLP Analysis**: Leverages `scikit-learn` to calculate the cosine similarity of text vectors, providing a mathematical basis for content overlap.
*   **OCR Capabilities**: Includes a `pytesseract` and `Pillow` service for future-proofing or manual image-to-text extraction tasks with pre-processing (upscaling/sharpening).

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Tesseract OCR** installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and populate it with your credentials:
```env
# Flask Settings
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true

# API Keys
PRIMARY_API_KEY=your_key
GENAI_API_KEY=your_google_key
SEARCH_ENGINE_ID=your_cse_id
SERPAPI_API_KEY=your_serp_key
```

---

## 🖥️ Usage

Start the server using the entry point:
```bash
python run.py
```

### API Endpoint: `POST /analyse`
Submit a URL to analyse its similarity against top search results.

**Request Body:**
```json
{
  "url": "https://example.com/article-to-check"
}
```

**Successful Response:**
```json
{
  "title_score": 0.8521,
  "description_score": 0.7240,
  "content_score": 0.6125,
  "overall_score": 0.7240,
  "sources_compared": 5
}
```

---

## 📂 Project Structure

*   `app/routes.py`: The primary controller managing the analysis workflow.
*   `app/services/scraper.py`: Contains `ContentSpider` and `WebScraper` logic, wrapping Scrapy in multiprocessing for stability.
*   `app/services/search_service.py`: Handles queries to external search engines.
*   `app/services/analyser.py`: Core logic for TF-IDF vectorization and cosine similarity calculations.
*   `app/services/ocr_service.py`: Image pre-processing and text extraction utilities.
*   `app/utils/helpers.py`: Domain filtering (e.g., skipping YouTube) and score aggregation logic.

---

## ⚙️ Technical Logic
The "Overall Score" is not a simple average. The application calculates the **mean** for each field (Title, Description, Paragraphs) across all comparison sources, and then calculates the **median** of those three means. This prevents a single missing field (like an empty meta-description) from disproportionately skewing the final result.

All similarity calculations utilise `cosine_similarity` on TF-IDF matrices:

$$\text{similarity} = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$$

---

## ⚖️ License
This project is provided for educational and analytical purposes. Ensure compliance with the `robots.txt` of target websites and the Terms of Service of the search providers (Google, SerpApi, DDG).
