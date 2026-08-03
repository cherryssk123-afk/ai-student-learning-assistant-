import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class='app.config.Config'):
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
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.tutor import tutor_bp
    from app.routes.notes import notes_bp
    from app.routes.planner import planner_bp
    from app.routes.assignment import assignment_bp
    from app.routes.exam import exam_bp
    from app.routes.resources import resources_bp
    from app.routes.feedback import feedback_bp

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
        db.create_all()

    return app
