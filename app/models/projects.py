import uuid

from sqlalchemy import func
from app.extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    # timesheets = db.relationship('Timesheet', back_populates='task')
    project = db.relationship('Project', back_populates='tasks')
    timesheet_entries = db.relationship('TimesheetEntry', back_populates='task', cascade='all, delete-orphan')



class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # tasks = db.relationship('Task', backref='project', lazy=True)
    tasks = db.relationship('Task', back_populates='project', lazy=True)
    timesheet_entries = db.relationship('TimesheetEntry', back_populates='project', lazy=True)

    # Relationships (lazy='select' so they are only loaded if accessed)
    created_by_user = db.relationship('User', back_populates='created_projects', foreign_keys=[created_by])
    updated_by_user = db.relationship('User', back_populates='updated_projects', foreign_keys=[updated_by])

