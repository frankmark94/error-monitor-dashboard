import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Application settings
    ENDPOINT_PATH = os.getenv('ENDPOINT_PATH', '/endpoint')
    MAX_LOGS = int(os.getenv('MAX_LOGS', '100'))
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))

    # Redis settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_LOGS_KEY = 'webhook_logs'
    REDIS_ERROR_CODES_KEY = 'error_codes'
    REDIS_CONNECTION_TYPES_KEY = 'connection_types'
    REDIS_HOURLY_ERRORS_KEY = 'hourly_errors'

config = Config() 