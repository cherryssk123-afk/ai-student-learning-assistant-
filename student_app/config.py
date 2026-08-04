import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'coventry_msc_dissertation_default_secret_key_2026')
    
    # SQLite Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Check if running on Vercel or read-only serverless environment
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/app.db'
    else:
        INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
        try:
            os.makedirs(INSTANCE_DIR, exist_ok=True)
            db_path = os.path.join(INSTANCE_DIR, 'app.db').replace('\\', '/')
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + db_path
        except OSError:
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/app.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 Hours
    
    # OpenAI API Key Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
