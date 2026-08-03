from datetime import datetime
from app import db
from app.models import LearningHistory, Achievement

def calculate_sus_score(responses):
    """
    Calculate System Usability Scale (SUS) Score based on 10 Likert responses (1 to 5).
    responses: list or dict with keys q1 to q10
    """
    if isinstance(responses, dict):
        q = [int(responses.get(f'q{i}', 3)) for i in range(1, 11)]
    else:
        q = [int(x) for x in responses]

    # Q1, Q3, Q5, Q7, Q9 (odd): score - 1
    # Q2, Q4, Q6, Q8, Q10 (even): 5 - score
    odd_sum = sum(q[i] - 1 for i in [0, 2, 4, 6, 8])
    even_sum = sum(5 - q[i] for i in [1, 3, 5, 7, 9])
    
    sus_score = (odd_sum + even_sum) * 2.5
    return round(sus_score, 1)

def get_sus_grade(score):
    if score >= 80.3:
        return 'A (Excellent - Grade A+ SaaS Standard)'
    elif score >= 68.0:
        return 'B (Good - High Acceptability)'
    elif score >= 51.0:
        return 'C (Fair - Marginal Acceptability)'
    else:
        return 'F (Unacceptable - Requires Optimization)'

def log_activity(user_id, activity_type, activity_title, details=""):
    """
    Log student activity to LearningHistory table.
    """
    try:
        history = LearningHistory(
            user_id=user_id,
            activity_type=activity_type,
            activity_title=activity_title,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")

def check_and_award_achievements(user):
    """
    Check student progress and award relevant academic achievement badges.
    """
    try:
        existing_badges = {a.badge_code for a in user.achievements.all()}
        new_unlocked = []

        # 1. First Roadmap Created
        if user.roadmaps.count() >= 1 and 'BADGE_ROADMAP_STARTER' not in existing_badges:
            b1 = Achievement(
                user_id=user.id,
                badge_code='BADGE_ROADMAP_STARTER',
                title='Pathway Pioneer',
                description='Generated your first AI-powered guided learning roadmap.',
                icon_class='bi-signpost-split'
            )
            db.session.add(b1)
            new_unlocked.append(b1.title)

        # 2. Roadmap Completed
        completed_roadmaps = user.roadmaps.filter_by(status='Completed').count()
        if completed_roadmaps >= 1 and 'BADGE_ROADMAP_MASTER' not in existing_badges:
            b2 = Achievement(
                user_id=user.id,
                badge_code='BADGE_ROADMAP_MASTER',
                title='Mastery Achieved',
                description='Successfully completed 100% of a guided learning roadmap!',
                icon_class='bi-trophy'
            )
            db.session.add(b2)
            new_unlocked.append(b2.title)

        # 3. AI Tutor Session
        if user.chats.count() >= 1 and 'BADGE_AI_TUTOR' not in existing_badges:
            b3 = Achievement(
                user_id=user.id,
                badge_code='BADGE_AI_TUTOR',
                title='Inquisitive Scholar',
                description='Consulted the AI Academic Tutor for deep conceptual learning.',
                icon_class='bi-robot'
            )
            db.session.add(b3)
            new_unlocked.append(b3.title)

        # 4. Study Plan Generated
        if user.study_plans.count() >= 1 and 'BADGE_PLANNER_PRO' not in existing_badges:
            b4 = Achievement(
                user_id=user.id,
                badge_code='BADGE_PLANNER_PRO',
                title='Strategist',
                description='Created a structured weekly study schedule.',
                icon_class='bi-calendar-check'
            )
            db.session.add(b4)
            new_unlocked.append(b4.title)

        # 5. SUS Feedback Submitted
        if user.feedbacks.count() >= 1 and 'BADGE_SUS_EVALUATOR' not in existing_badges:
            b5 = Achievement(
                user_id=user.id,
                badge_code='BADGE_SUS_EVALUATOR',
                title='Research Evaluator',
                description='Participated in the MSc System Usability Scale (SUS) research evaluation.',
                icon_class='bi-check-circle'
            )
            db.session.add(b5)
            new_unlocked.append(b5.title)

        if new_unlocked:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error evaluating achievements: {e}")
