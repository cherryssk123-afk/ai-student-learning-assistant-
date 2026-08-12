import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class='student_app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access your learning portal.'
    login_manager.login_message_category = 'warning'

    # Register Blueprints
    from student_app.routes.main import main_bp
    from student_app.routes.auth import auth_bp
    from student_app.routes.roadmap import roadmap_bp
    from student_app.routes.tutor import tutor_bp
    from student_app.routes.notes import notes_bp
    from student_app.routes.planner import planner_bp
    from student_app.routes.assignment import assignment_bp
    from student_app.routes.exam import exam_bp
    from student_app.routes.resources import resources_bp
    from student_app.routes.feedback import feedback_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(roadmap_bp, url_prefix='/roadmap')
    app.register_blueprint(tutor_bp, url_prefix='/tutor')
    app.register_blueprint(notes_bp, url_prefix='/notes')
    app.register_blueprint(planner_bp, url_prefix='/planner')
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(resources_bp, url_prefix='/resources')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')

    # Create database tables if they do not exist
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

    # Global exception handler to catch any unhandled 500 errors gracefully
    @app.errorhandler(500)
    def handle_500_error(e):
        try:
            db.session.rollback()
        except Exception:
            pass
        from flask import redirect, url_for
        return redirect(url_for('main.index'))

    # Inject No-Cache headers to prevent browsers from caching old error pages
    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app
