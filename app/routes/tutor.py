from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, csrf
from app.models import TutorChat
from app.utils.ai_service import ai_service
from app.utils.helpers import log_activity, check_and_award_achievements

tutor_bp = Blueprint('tutor', __name__)

@tutor_bp.route('/', methods=['GET'])
@login_required
def index():
    # Fetch or create current user active tutor session
    chat_session = TutorChat.query.filter_by(user_id=current_user.id).order_by(TutorChat.updated_at.desc()).first()
    if not chat_session:
        chat_session = TutorChat(user_id=current_user.id, session_title='Academic AI Study Session')
        db.session.add(chat_session)
        db.session.commit()

    messages = chat_session.get_messages()
    return render_template('tutor.html', chat_session=chat_session, messages=messages)

@tutor_bp.route('/ask', methods=['POST'])
@csrf.exempt
@login_required
def ask():
    if request.is_json:
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        topic_context = data.get('context', 'General Higher Education Academic Topic').strip()
    else:
        question = request.form.get('question', '').strip()
        topic_context = request.form.get('context', 'General Higher Education Academic Topic').strip()

    if not question:
        if not request.is_json:
            flash('Question cannot be empty.', 'danger')
            return redirect(url_for('tutor.index'))
        return jsonify({'success': False, 'error': 'Question cannot be empty.'}), 400

    chat_session = TutorChat.query.filter_by(user_id=current_user.id).order_by(TutorChat.updated_at.desc()).first()
    if not chat_session:
        chat_session = TutorChat(user_id=current_user.id, session_title=f'Study Session: {question[:30]}')
        db.session.add(chat_session)

    history = chat_session.get_messages()
    
    # User message
    user_msg = {
        'role': 'user',
        'content': question,
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }
    history.append(user_msg)

    # AI Tutor answer
    ai_answer = ai_service.ask_tutor(question, chat_history=history, context_topic=topic_context)
    
    assistant_msg = {
        'role': 'assistant',
        'content': ai_answer,
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }
    history.append(assistant_msg)

    chat_session.set_messages(history)
    chat_session.updated_at = datetime.utcnow()
    db.session.commit()

    log_activity(current_user.id, 'Tutor', 'Asked AI Tutor', f'Question: "{question[:50]}..."')
    check_and_award_achievements(current_user)

    if not request.is_json:
        return redirect(url_for('tutor.index'))

    return jsonify({
        'success': True,
        'answer': ai_answer,
        'timestamp': assistant_msg['timestamp']
    })

@tutor_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    chat_session = TutorChat.query.filter_by(user_id=current_user.id).order_by(TutorChat.updated_at.desc()).first()
    if chat_session:
        chat_session.set_messages([])
        db.session.commit()
        flash('AI Tutor chat history reset.', 'info')
    return redirect(url_for('tutor.index'))
