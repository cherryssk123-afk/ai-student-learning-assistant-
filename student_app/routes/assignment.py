from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity

assignment_bp = Blueprint('assignment', __name__)

@assignment_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    guidance = None
    topic = ""
    level = "Postgraduate (MSc)"

    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        level = request.form.get('level', 'Postgraduate (MSc)').strip()

        if not topic:
            flash('Please specify an assignment topic.', 'danger')
        else:
            guidance = ai_service.generate_assignment_guidance(topic, level)
            log_activity(current_user.id, 'Assignment', 'Generated Assignment Guidance', f'Structured framework for "{topic}".')
            flash('Assignment guidance generated in compliance with Coventry University Academic Integrity Guidelines.', 'success')

    return render_template('assignment.html', guidance=guidance, topic=topic, level=level)
