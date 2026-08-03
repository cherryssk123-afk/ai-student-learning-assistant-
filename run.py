import os
import sys

# Get absolute path of current file's directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 1. Ensure BASE_DIR is at the top of sys.path
if BASE_DIR in sys.path:
    sys.path.remove(BASE_DIR)
sys.path.insert(0, BASE_DIR)

# 2. Check for subfolders containing 'app' package
for root, dirs, files in os.walk(BASE_DIR):
    if 'app' in dirs and os.path.exists(os.path.join(root, 'app', '__init__.py')):
        if root in sys.path:
            sys.path.remove(root)
        sys.path.insert(0, root)
        break

# 3. Unbind Gunicorn internal 'app' module conflict if loaded in sys.modules
if 'app' in sys.modules:
    mod = sys.modules['app']
    if not hasattr(mod, 'create_app'):
        del sys.modules['app']

from dotenv import load_dotenv
load_dotenv()

# 4. Import application factory
try:
    from app import create_app, db
except (ImportError, ModuleNotFoundError):
    if 'app' in sys.modules:
        del sys.modules['app']
    from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("================================================================")
    print(" AI-Powered Student Learning Assistant for Higher Education")
    print(" Coventry University MSc Dissertation Project")
    print(" Server running at: http://127.0.0.1:5000")
    print("================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
