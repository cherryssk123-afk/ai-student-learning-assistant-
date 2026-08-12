from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from student_app import db, csrf
from student_app.models import User
from student_app.utils.helpers import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        university = request.form.get('university', 'Coventry University').strip()
        degree_program = request.form.get('degree_program', 'Computer Science').strip()

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered. Please log in.', 'danger')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            university=university,
            degree_program=degree_program
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        log_activity(user.id, 'Authentication', 'Registered Account', f'Registered with email {email}')
        login_user(user)
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email
        session['university'] = user.university
        session['degree_program'] = user.degree_program
        flash('Welcome to AI-Powered Student Learning Assistant! Your account has been created.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        if not identifier or not password:
            flash('Please enter your username or email and password.', 'danger')
            return render_template('auth/login.html')

        try:
            db.create_all()
        except Exception:
            pass

        # Case-insensitive lookup for username or email
        user = User.query.filter(
            (db.func.lower(User.username) == identifier.lower()) | 
            (db.func.lower(User.email) == identifier.lower())
        ).first()

        if user:
            # Existing user found -> verify password
            if user.check_password(password):
                login_user(user, remember=remember)
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                session['university'] = user.university
                session['degree_program'] = user.degree_program
                
                log_activity(user.id, 'Authentication', 'Logged In', 'Successful login session started.')
                flash(f'Welcome back, {user.username}!', 'success')
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
                return render_template('auth/login.html')
        else:
            # Provision account for this student on fresh serverless pods
            clean_username = identifier.split('@')[0] if '@' in identifier else identifier
            clean_email = identifier.lower() if '@' in identifier else f"{identifier.lower()}@coventry.ac.uk"
            
            user = User.query.filter(
                (db.func.lower(User.username) == clean_username.lower()) | 
                (db.func.lower(User.email) == clean_email)
            ).first()

            if not user:
                user = User(
                    username=clean_username,
                    email=clean_email,
                    university='Coventry University',
                    degree_program='Higher Education Studies'
                )
                user.set_password(password)
                try:
                    db.session.add(user)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    user = User.query.filter(
                        (db.func.lower(User.username) == clean_username.lower()) | 
                        (db.func.lower(User.email) == clean_email)
                    ).first()

            if user and user.check_password(password):
                login_user(user, remember=remember)
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                session['university'] = user.university
                session['degree_program'] = user.degree_program
                
                log_activity(user.id, 'Authentication', 'Logged In', 'Successful login session started.')
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid login credentials. Please check your username/password or register.', 'danger')
                return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    try:
        if current_user.is_authenticated:
            log_activity(current_user.id, 'Authentication', 'Logged Out', 'User ended session.')
    except Exception:
        pass

    logout_user()
    session.clear()
    session.permanent = False
    
    flash('You have been logged out successfully.', 'info')
    
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('session', '', expires=0, path='/')
    resp.set_cookie('remember_token', '', expires=0, path='/')
    return resp
