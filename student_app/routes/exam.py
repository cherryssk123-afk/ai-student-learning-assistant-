from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    prep_data = None
    topic = ""
    level = "Intermediate"

    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        level = request.form.get('level', 'Intermediate').strip()

        if not topic:
            flash('Please enter your revision topic.', 'danger')
        else:
            prep_data = ai_service.generate_exam_prep(topic, level)
            log_activity(current_user.id, 'Exam', 'Generated Exam Revision Kit', f'Created revision kit for "{topic}".')
            flash('Exam preparation kit and practice questions generated!', 'success')

    return render_template('exam.html', prep_data=prep_data, topic=topic, level=level)
