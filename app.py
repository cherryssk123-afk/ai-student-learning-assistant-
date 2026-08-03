import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR in sys.path:
    sys.path.remove(BASE_DIR)
sys.path.insert(0, BASE_DIR)

for root, dirs, files in os.walk(BASE_DIR):
    if 'app' in dirs and os.path.exists(os.path.join(root, 'app', '__init__.py')):
        if root in sys.path:
            sys.path.remove(root)
        sys.path.insert(0, root)
        break

if 'app' in sys.modules:
    mod = sys.modules['app']
    if not hasattr(mod, 'create_app'):
        del sys.modules['app']

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
