from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity

from student_app import csrf

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    resources_data = None
    topic = "Machine Learning"

    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        if not topic:
            flash('Please enter a topic to search resources.', 'danger')
        else:
            resources_data = ai_service.recommend_resources(topic)
            try:
                if current_user and hasattr(current_user, 'id'):
                    log_activity(current_user.id, 'Resources', 'Searched Academic Resources', f'Found resources for "{topic}".')
            except Exception as e:
                print(f"Resources logging warning: {e}")
    else:
        resources_data = ai_service.recommend_resources(topic)

    return render_template('resources.html', resources_data=resources_data, topic=topic)
