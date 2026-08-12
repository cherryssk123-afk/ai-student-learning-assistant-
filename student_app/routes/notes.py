from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity, check_and_award_achievements

from student_app import csrf

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    summary_data = None
    raw_notes = ""

    if request.method == 'POST':
        raw_notes = request.form.get('raw_notes', '').strip()
        if not raw_notes:
            flash('Please paste or type lecture notes to summarize.', 'danger')
        else:
            summary_data = ai_service.summarize_notes(raw_notes)
            try:
                if current_user and hasattr(current_user, 'id'):
                    log_activity(current_user.id, 'Notes', 'Summarized Lecture Notes', f'Summarized {len(raw_notes.split())} words of study material.')
                    check_and_award_achievements(current_user)
            except Exception as e:
                print(f"Notes logging warning: {e}")
            flash('Notes summarized successfully into executive takeaways and flashcards!', 'success')

    return render_template('notes.html', summary_data=summary_data, raw_notes=raw_notes)
