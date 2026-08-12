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

    login_manager.login_view = 'main.dashboard'
    login_manager.login_message = None

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

    # Instant Direct Access Middleware - Auto-logs in every visitor as an active student!
    @app.before_request
    def ensure_instant_access():
        from flask import request, session
        from flask_login import current_user, login_user
        from student_app.models import User
        
        if request.endpoint and ('static' in request.endpoint or 'auth.logout' in request.endpoint):
            return
            
        if not current_user.is_authenticated:
            try:
                db.create_all()
                user_name = session.get('username', 'Student User')
                safe_name = user_name.replace(' ', '_').lower()
                user_email = session.get('email', f"{safe_name}@coventry.ac.uk")
                
                user = User.query.filter((User.username == user_name) | (User.email == user_email)).first()
                if not user:
                    user = User(
                        username=user_name,
                        email=user_email,
                        university=session.get('university', 'Coventry University'),
                        degree_program=session.get('degree_program', 'MSc Dissertation Studies')
                    )
                    user.set_password('password123')
                    db.session.add(user)
                    db.session.commit()
                
                login_user(user, remember=True)
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
            except Exception as e:
                print(f"Instant access middleware warning: {e}")
                db.session.rollback()

    # Global exception handler to catch any unhandled 500 errors gracefully
    @app.errorhandler(500)
    def handle_500_error(e):
        try:
            db.session.rollback()
        except Exception:
            pass
        from flask import redirect, url_for
        return redirect(url_for('main.dashboard'))

    # Inject No-Cache headers to prevent browsers from caching old error pages
    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app
