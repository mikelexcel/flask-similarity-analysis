import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    PRIMARY_API_KEY = os.environ.get('PRIMARY_API_KEY')
    SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
    GENAI_API_KEY = os.environ.get('GENAI_API_KEY')
    SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID')

    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT  = int(os.environ.get('FLASK_PORT', 5000))
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'