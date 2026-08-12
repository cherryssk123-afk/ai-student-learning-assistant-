import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from student_app import db
from student_app.models import LearningRoadmap, RoadmapWeek
from student_app.utils.ai_service import ai_service
from student_app.utils.helpers import log_activity, check_and_award_achievements

from student_app import db, csrf

roadmap_bp = Blueprint('roadmap', __name__)

@roadmap_bp.route('/create', methods=['GET', 'POST'])
@csrf.exempt
def create():
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        level = request.form.get('level', 'Beginner').strip()
        purpose = request.form.get('purpose', 'Skill Development').strip()
        hours = request.form.get('hours', type=int, default=10)

        if not topic:
            flash('Please enter what you want to learn.', 'danger')
            return render_template('roadmap/create.html')

        # Call AI Service to generate multi-week structure
        ai_data = ai_service.generate_learning_roadmap(topic, level, purpose, hours)
        
        weeks_data = ai_data.get('weeks', [])
        total_weeks = ai_data.get('total_weeks', len(weeks_data))

        # Create Roadmap model
        roadmap = LearningRoadmap(
            user_id=current_user.id,
            topic=topic,
            level=level,
            purpose=purpose,
            hours_per_week=hours,
            total_weeks=total_weeks,
            progress_percent=0.0,
            status='In Progress'
        )
        db.session.add(roadmap)
        db.session.flush()  # Get roadmap.id

        # Save week records
        for week_info in weeks_data:
            week = RoadmapWeek(
                roadmap_id=roadmap.id,
                week_number=week_info.get('week_number', 1),
                title=week_info.get('title', f"Week {week_info.get('week_number')}"),
                description=week_info.get('description', ''),
                key_topics=json.dumps(week_info.get('key_topics', [])),
                tasks=json.dumps(week_info.get('tasks', [])),
                is_completed=False
            )
            db.session.add(week)

        db.session.commit()
        log_activity(current_user.id, 'Roadmap', 'Generated Learning Pathway', f'Created {total_weeks}-week roadmap for "{topic}" ({level}).')
        check_and_award_achievements(current_user)

        flash(f'Your custom {total_weeks}-week learning roadmap for "{topic}" is ready!', 'success')
        return redirect(url_for('roadmap.view', roadmap_id=roadmap.id))

    return render_template('roadmap/create.html')

@roadmap_bp.route('/<int:roadmap_id>')
def view(roadmap_id):
    try:
        roadmap = LearningRoadmap.query.get(roadmap_id)
        if not roadmap or roadmap.user_id != current_user.id:
            flash('Roadmap not found or access expired.', 'warning')
            return redirect(url_for('main.dashboard'))
        return render_template('roadmap/view.html', roadmap=roadmap)
    except Exception as e:
        print(f"Roadmap view fallback: {e}")
        return redirect(url_for('main.dashboard'))

@roadmap_bp.route('/<int:roadmap_id>/toggle-week/<int:week_id>', methods=['POST'])
@csrf.exempt
def toggle_week(roadmap_id, week_id):
    try:
        roadmap = LearningRoadmap.query.get(roadmap_id)
        if not roadmap or roadmap.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized or roadmap missing'}), 403

        week = RoadmapWeek.query.get(week_id)
        if not week or week.roadmap_id != roadmap.id:
            return jsonify({'success': False, 'error': 'Invalid week'}), 400

        week.is_completed = not week.is_completed
        tasks = week.get_tasks()
        for task in tasks:
            task['done'] = week.is_completed
        week.tasks = json.dumps(tasks)

        progress = roadmap.recalculate_progress()
        db.session.commit()

        log_activity(current_user.id, 'Roadmap', 'Updated Milestone', f'Marked Week {week.week_number} of "{roadmap.topic}" as {"Completed" if week.is_completed else "Incomplete"}.')
        check_and_award_achievements(current_user)

        return jsonify({
            'success': True,
            'week_completed': week.is_completed,
            'progress_percent': progress,
            'status': roadmap.status
        })
    except Exception as e:
        print(f"Toggle week fallback: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Error updating database.'}), 500

@roadmap_bp.route('/<int:roadmap_id>/delete', methods=['POST'])
@csrf.exempt
def delete(roadmap_id):
    try:
        roadmap = LearningRoadmap.query.get(roadmap_id)
        if roadmap and roadmap.user_id == current_user.id:
            topic = roadmap.topic
            db.session.delete(roadmap)
            db.session.commit()
            flash(f'Learning roadmap for "{topic}" has been removed.', 'info')
    except Exception as e:
        print(f"Roadmap delete fallback: {e}")
        db.session.rollback()
    return redirect(url_for('main.dashboard'))
