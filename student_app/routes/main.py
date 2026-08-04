from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from student_app.models import LearningRoadmap, StudyPlan, TutorChat, Feedback, Achievement, LearningHistory
from student_app.utils.helpers import check_and_award_achievements
from student_app.utils.ai_service import ai_service

main_bp = Blueprint('main', __name__)

@main_bp.app_context_processor
def inject_ai_mode():
    return dict(ai_mode=ai_service.get_active_mode())

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/set-api-key', methods=['POST'])
def set_api_key():
    key = request.form.get('api_key', '').strip()
    if key:
        session['openai_api_key'] = key
        flash('OpenAI API Key connected successfully for your session!', 'success')
    else:
        session.pop('openai_api_key', None)
        flash('OpenAI API Key cleared. System running on Smart Local AI Engine.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Evaluate achievements
    check_and_award_achievements(current_user)
    
    roadmaps = current_user.roadmaps.order_by(LearningRoadmap.created_at.desc()).all()
    active_roadmap = current_user.roadmaps.filter(LearningRoadmap.status != 'Completed').order_by(LearningRoadmap.created_at.desc()).first()
    recent_study_plan = current_user.study_plans.order_by(StudyPlan.created_at.desc()).first()
    recent_history = current_user.history.order_by(LearningHistory.timestamp.desc()).limit(6).all()
    achievements = current_user.achievements.order_by(Achievement.unlocked_at.desc()).all()
    
    total_roadmaps = len(roadmaps)
    completed_roadmaps = sum(1 for r in roadmaps if r.status == 'Completed')
    total_chats = current_user.chats.count()
    has_feedback = current_user.feedbacks.count() > 0

    return render_template(
        'dashboard.html',
        roadmaps=roadmaps,
        active_roadmap=active_roadmap,
        recent_study_plan=recent_study_plan,
        recent_history=recent_history,
        achievements=achievements,
        total_roadmaps=total_roadmaps,
        completed_roadmaps=completed_roadmaps,
        total_chats=total_chats,
        has_feedback=has_feedback
    )

@main_bp.route('/profile')
@login_required
def profile():
    roadmaps = current_user.roadmaps.all()
    achievements = current_user.achievements.all()
    history = current_user.history.order_by(LearningHistory.timestamp.desc()).all()
    feedbacks = current_user.feedbacks.order_by(Feedback.created_at.desc()).all()
    
    return render_template(
        'profile.html',
        roadmaps=roadmaps,
        achievements=achievements,
        history=history,
        feedbacks=feedbacks
    )

