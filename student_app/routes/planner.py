import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from student_app import db
from student_app.models import StudyPlan
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity, check_and_award_achievements

from student_app import csrf

planner_bp = Blueprint('planner', __name__)

@planner_bp.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    study_plans = []
    try:
        if current_user and hasattr(current_user, 'study_plans'):
            study_plans = current_user.study_plans.order_by(StudyPlan.created_at.desc()).all()
    except Exception:
        study_plans = []
        
    active_plan = study_plans[0] if study_plans else None

    if request.method == 'POST':
        raw_subjects = request.form.get('subjects', '').strip()
        hours = request.form.get('hours', type=int, default=15)
        deadline = request.form.get('deadline', '').strip()

        if not raw_subjects:
            flash('Please enter at least one module or subject.', 'danger')
            return render_template('planner.html', study_plans=study_plans, active_plan=active_plan)

        subjects = [s.strip() for s in raw_subjects.split(',') if s.strip()]
        plan_data = ai_service.generate_study_plan(subjects, hours, deadline)

        try:
            if current_user and hasattr(current_user, 'id'):
                study_plan = StudyPlan(
                    user_id=current_user.id,
                    title=f"Weekly Plan: {', '.join(subjects[:2])}",
                    available_hours=hours,
                    deadline_date=deadline,
                    subjects_json=json.dumps(subjects),
                    schedule_json=json.dumps(plan_data)
                )
                db.session.add(study_plan)
                db.session.commit()
                log_activity(current_user.id, 'Planner', 'Created Study Plan', f'Allocated {hours} hours across {len(subjects)} subjects.')
                check_and_award_achievements(current_user)
        except Exception as e:
            print(f"Planner save warning: {e}")
            db.session.rollback()

        flash('Your weekly study schedule has been generated!', 'success')
        return render_template('planner.html', study_plans=study_plans, active_plan={'title': f"Weekly Plan: {', '.join(subjects[:2])}", 'schedule_json': json.dumps(plan_data), 'get_schedule': lambda: plan_data, 'get_subjects': lambda: subjects})

    return render_template('planner.html', study_plans=study_plans, active_plan=active_plan)
