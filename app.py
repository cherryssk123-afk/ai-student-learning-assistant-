import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

for root, dirs, files in os.walk(BASE_DIR):
    if 'app' in dirs and os.path.exists(os.path.join(root, 'app', '__init__.py')):
        if root not in sys.path:
            sys.path.insert(0, root)
        break

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
