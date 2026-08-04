from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from student_app import db
from student_app.models import Feedback
from student_app.utils.helpers import calculate_sus_score, get_sus_grade, log_activity, check_and_award_achievements

feedback_bp = Blueprint('feedback', __name__)

# Standard System Usability Scale (SUS) 10 Questions
SUS_QUESTIONS = [
    {"id": "q1", "text": "I think that I would like to use this system frequently for my university studies."},
    {"id": "q2", "text": "I found the system unnecessarily complex."},
    {"id": "q3", "text": "I thought the system was easy to use."},
    {"id": "q4", "text": "I think that I would need the support of a technical person to be able to use this system."},
    {"id": "q5", "text": "I found the various functions in this system were well integrated."},
    {"id": "q6", "text": "I thought there was too much inconsistency in this system."},
    {"id": "q7", "text": "I would imagine that most university students would learn to use this system very quickly."},
    {"id": "q8", "text": "I found the system very cumbersome to use."},
    {"id": "q9", "text": "I felt very confident using the system."},
    {"id": "q10", "text": "I needed to learn a lot of things before I could get going with this system."}
]

@feedback_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    try:
        user_feedbacks = current_user.feedbacks.order_by(Feedback.created_at.desc()).all()
        latest_feedback = user_feedbacks[0] if user_feedbacks else None
        all_feedbacks = Feedback.query.all()
        avg_sus = round(sum(f.sus_score for f in all_feedbacks) / len(all_feedbacks), 1) if all_feedbacks else 0.0
    except Exception as e:
        print(f"Feedback query fallback: {e}")
        user_feedbacks, latest_feedback, avg_sus = [], None, 0.0

    if request.method == 'POST':
        try:
            q_responses = [int(request.form.get(f'q{i}', 3)) for i in range(1, 11)]
            star_rating = int(request.form.get('star_rating', 5))
            written_feedback = request.form.get('written_feedback', '').strip()

            sus_score = calculate_sus_score(q_responses)

            feedback_entry = Feedback(
                user_id=current_user.id,
                q1=q_responses[0],
                q2=q_responses[1],
                q3=q_responses[2],
                q4=q_responses[3],
                q5=q_responses[4],
                q6=q_responses[5],
                q7=q_responses[6],
                q8=q_responses[7],
                q9=q_responses[8],
                q10=q_responses[9],
                sus_score=sus_score,
                star_rating=star_rating,
                written_feedback=written_feedback
            )
            db.session.add(feedback_entry)
            db.session.commit()

            grade = get_sus_grade(sus_score)
            log_activity(current_user.id, 'Feedback', 'Submitted SUS Evaluation', f'Computed SUS Score: {sus_score}/100 ({grade})')
            check_and_award_achievements(current_user)

            flash(f'Thank you! Your System Usability Scale (SUS) score is {sus_score}/100 ({grade}). Response recorded for dissertation analysis.', 'success')
            return redirect(url_for('feedback.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting survey: {e}', 'danger')

    return render_template(
        'feedback.html',
        questions=SUS_QUESTIONS,
        user_feedbacks=user_feedbacks,
        latest_feedback=latest_feedback,
        avg_sus=avg_sus,
        get_sus_grade=get_sus_grade
    )
