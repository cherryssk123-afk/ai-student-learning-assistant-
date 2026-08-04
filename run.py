import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from student_app import create_app, db

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
