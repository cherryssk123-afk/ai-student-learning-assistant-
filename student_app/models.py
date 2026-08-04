from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from student_app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    university = db.Column(db.String(120), default='Coventry University')
    degree_program = db.Column(db.String(120), default='Computer Science')
    study_year = db.Column(db.String(30), default='Postgraduate (MSc)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmaps = db.relationship('LearningRoadmap', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    study_plans = db.relationship('StudyPlan', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    chats = db.relationship('TutorChat', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('LearningHistory', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class LearningRoadmap(db.Model):
    __tablename__ = 'learning_roadmaps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(30), nullable=False)  # Beginner, Intermediate, Advanced
    purpose = db.Column(db.String(50), nullable=False)  # Exam, Assignment, Skill Development
    hours_per_week = db.Column(db.Integer, default=10)
    total_weeks = db.Column(db.Integer, default=6)
    progress_percent = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='In Progress')  # In Progress, Completed, Paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    weeks = db.relationship('RoadmapWeek', backref='roadmap', lazy='joined', cascade='all, delete-orphan', order_by='RoadmapWeek.week_number')

    def recalculate_progress(self):
        if not self.weeks:
            self.progress_percent = 0.0
            return 0.0
        completed = sum(1 for w in self.weeks if w.is_completed)
        self.progress_percent = round((completed / len(self.weeks)) * 100, 1)
        if self.progress_percent >= 100.0:
            self.status = 'Completed'
        return self.progress_percent


class RoadmapWeek(db.Model):
    __tablename__ = 'roadmap_weeks'
    
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('learning_roadmaps.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    key_topics = db.Column(db.Text, nullable=True)  # JSON array string
    tasks = db.Column(db.Text, nullable=True)       # JSON array string of objects [{id, text, done}]
    is_completed = db.Column(db.Boolean, default=False)
    
    def get_key_topics(self):
        return json.loads(self.key_topics) if self.key_topics else []

    def get_tasks(self):
        return json.loads(self.tasks) if self.tasks else []


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    available_hours = db.Column(db.Integer, nullable=False)
    deadline_date = db.Column(db.String(50), nullable=True)
    subjects_json = db.Column(db.Text, nullable=False)    # JSON array of subject names
    schedule_json = db.Column(db.Text, nullable=False)    # JSON structured schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_subjects(self):
        return json.loads(self.subjects_json) if self.subjects_json else []

    def get_schedule(self):
        return json.loads(self.schedule_json) if self.schedule_json else {}


class TutorChat(db.Model):
    __tablename__ = 'tutor_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_title = db.Column(db.String(150), default='AI Study Session')
    messages_json = db.Column(db.Text, default='[]')  # JSON array of message objects {role, content, timestamp}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_messages(self):
        return json.loads(self.messages_json) if self.messages_json else []

    def set_messages(self, messages):
        self.messages_json = json.dumps(messages)


class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # SUS Questions Q1 to Q10 (1-5 Likert scale)
    q1 = db.Column(db.Integer, nullable=False)
    q2 = db.Column(db.Integer, nullable=False)
    q3 = db.Column(db.Integer, nullable=False)
    q4 = db.Column(db.Integer, nullable=False)
    q5 = db.Column(db.Integer, nullable=False)
    q6 = db.Column(db.Integer, nullable=False)
    q7 = db.Column(db.Integer, nullable=False)
    q8 = db.Column(db.Integer, nullable=False)
    q9 = db.Column(db.Integer, nullable=False)
    q10 = db.Column(db.Integer, nullable=False)
    
    sus_score = db.Column(db.Float, nullable=False)  # 0 to 100
    star_rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    written_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LearningHistory(db.Model):
    __tablename__ = 'learning_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # Roadmap, Tutor, Notes, Planner, Assignment, Exam, Feedback
    activity_title = db.Column(db.String(150), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_code = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon_class = db.Column(db.String(50), default='bi-award')
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
