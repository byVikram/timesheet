
import uuid

# from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON, func

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
    timesheet_entries = db.relationship('TimesheetEntry', back_populates='status_obj')
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

    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)

    status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


    # Relationships
    user = db.relationship('User', back_populates='created_timesheets', foreign_keys=[user_id])
    status_obj = db.relationship('TimesheetStatus')
    entries = db.relationship('TimesheetEntry', back_populates='timesheet', cascade='all, delete-orphan')



class TimesheetEntry(db.Model):
    __tablename__ = 'timesheet_entries'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    timesheet_id = db.Column(db.Integer, db.ForeignKey('timesheets.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    hours = db.Column(db.Float, nullable=False)
    time_records = db.Column(JSON, nullable=False)
    status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'), nullable=False)

    status_obj = db.relationship('TimesheetStatus', back_populates='timesheet_entries')


    # Relationships
    approver = db.relationship('User', back_populates='approved_timesheets_entries', foreign_keys=[approver_id])
    timesheet = db.relationship('Timesheet', back_populates='entries')
    project = db.relationship('Project', back_populates='timesheet_entries')
    task = db.relationship('Task', back_populates='timesheet_entries')

    history = db.relationship('TimesheetHistory', back_populates='timesheet_entry')




# ---------------------------
# Timesheet History
# ---------------------------
class TimesheetHistory(db.Model):
    __tablename__ = 'timesheet_history'

    id = db.Column(db.Integer, primary_key=True)
    timesheet_entry_id = db.Column(db.Integer, db.ForeignKey('timesheet_entries.id'), nullable=False)
    old_status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'))
    new_status = db.Column(db.Integer, db.ForeignKey('timesheet_status.id'))
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)

    # Relationships
    timesheet_entry  = db.relationship('TimesheetEntry', back_populates='history')
    old_status_obj = db.relationship('TimesheetStatus', foreign_keys=[old_status], back_populates='history_old')
    new_status_obj = db.relationship('TimesheetStatus', foreign_keys=[new_status], back_populates='history_new')
    changed_by_user = db.relationship('User', back_populates='changed_timesheets')


