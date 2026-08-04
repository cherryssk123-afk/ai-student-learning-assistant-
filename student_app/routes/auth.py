from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from student_app import db
from student_app.models import User
from student_app.utils.helpers import log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
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
        flash('Welcome to AI-Powered Student Learning Assistant! Your account has been created.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email.lower())).first()

        if not user or not user.check_password(password):
            flash('Invalid username/email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        log_activity(user.id, 'Authentication', 'Logged In', 'Successful login session started.')
        flash(f'Welcome back, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'Authentication', 'Logged Out', 'User ended session.')
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
