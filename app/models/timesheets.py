from datetime import datetime
import uuid

# from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON, func
from sqlalchemy.ext.mutable import MutableList

# from sqlalchemy import JSON
from app.extensions import db

class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)


    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)



    # organization = db.relationship('Organization', back_populates='holidays', lazy=True)


# ---------------------------
# Timesheet Status
# ---------------------------
class TimesheetStatus(db.Model):
    __tablename__ = 'timesheet_status'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Relationships
    timesheets = db.relationship('Timesheet', back_populates='status_obj')
    # approvals = db.relationship('TimesheetApproval', back_populates='status_obj')
    history_old = db.relationship('TimesheetHistory', back_populates='old_status_obj', foreign_keys='TimesheetHistory.old_status')
    history_new = db.relationship('TimesheetHistory', back_populates='new_status_obj', foreign_keys='TimesheetHistory.new_status')


# ---------------------------
# Timesheet
# ---------------------------
class Timesheet(db.Model):
    __tablename__ = 'timesheets'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True) 
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    
    week_start = db.Column(db.Date, nullable=False)  # Monday of the week
    week_end = db.Column(db.Date, nullable=False)    # Sunday of the week

    time_records = db.Column(JSON, nullable=False)   # JSON storing 7 days of data
    # time_records = db.Column(MutableList.as_mutable(JSON), nullable=False)

    status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


    # Relationships
    user = db.relationship('User', back_populates='created_timesheets', foreign_keys=[user_id])
    approver = db.relationship('User', back_populates='approved_timesheets', foreign_keys=[approver_id])
    # approvals = db.relationship('TimesheetApproval', back_populates='timesheet', cascade='all, delete-orphan')
    project = db.relationship('Project', back_populates='timesheets')
    tasks = db.relationship('Task', back_populates='task_timesheet')
    history = db.relationship('TimesheetHistory', back_populates='timesheet')
    status_obj = db.relationship('TimesheetStatus')



# ---------------------------
# Timesheet History
# ---------------------------
class TimesheetHistory(db.Model):
    __tablename__ = 'timesheet_history'

    id = db.Column(db.Integer, primary_key=True)
    timesheet_id = db.Column(db.Integer, db.ForeignKey('timesheets.id'), nullable=False)
    old_status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'))
    new_status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'))
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


    # Relationships
    timesheet = db.relationship('Timesheet', back_populates='history')
    old_status_obj = db.relationship('TimesheetStatus', foreign_keys=[old_status], back_populates='history_old')
    new_status_obj = db.relationship('TimesheetStatus', foreign_keys=[new_status], back_populates='history_new')
    changed_by_user = db.relationship('User', back_populates='changed_timesheets')


