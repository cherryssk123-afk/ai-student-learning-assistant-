import os
import sys

# Add project root directory to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv()

from student_app import create_app, db

app = create_app()

@app.before_request
def initialize_database_once():
    if not getattr(app, '_got_db_init', False):
        try:
            db.create_all()
            app._got_db_init = True
        except Exception as e:
            print(f"Database init warning: {e}")
