import os
import sys

# Get absolute path of current file's directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Search paths for module resolution
search_paths = [
    current_dir,
    os.path.join(current_dir, 'anti gravity'),
    os.path.join(current_dir, 'anti-gravity'),
    os.path.join(current_dir, 'src'),
]

# Search for any directory containing 'app' package
for root, dirs, files in os.walk(current_dir):
    if 'app' in dirs:
        if os.path.exists(os.path.join(root, 'app', '__init__.py')):
            if root not in search_paths:
                search_paths.insert(0, root)

for path in search_paths:
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)

from dotenv import load_dotenv
load_dotenv()

try:
    from app import create_app, db
except ModuleNotFoundError:
    # Deep fallback search across current working directory
    for root, dirs, files in os.walk(os.path.abspath(os.curdir)):
        if 'app' in dirs and os.path.exists(os.path.join(root, 'app', '__init__.py')):
            sys.path.insert(0, root)
            break
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
