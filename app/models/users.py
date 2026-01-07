
import uuid

from sqlalchemy import func
from app.extensions import db


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


    users = db.relationship('User', back_populates='organization', lazy=True)


# class Designation(db.Model):
#     __tablename__ = 'designations'

#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
#     name = db.Column(db.String(100), unique=True, nullable=False)
#     description = db.Column(db.Text)

#     created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
#     updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)





class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
    reporting_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Self-referential FK

    full_name = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


    organization = db.relationship('Organization', back_populates='users', lazy=True)
    role = db.relationship('UserRole', back_populates='users', lazy=True)
    created_timesheets = db.relationship('Timesheet', back_populates='user', foreign_keys='Timesheet.user_id', lazy=True)
    approved_timesheets_entries = db.relationship('TimesheetEntry', back_populates='approver', foreign_keys='TimesheetEntry.approver_id', lazy=True)
    changed_timesheets = db.relationship('TimesheetHistory', back_populates='changed_by_user', lazy=True)
    manager = db.relationship('User', remote_side=[id], backref='subordinates', lazy=True)

    subscriptions = db.relationship("PushSubscription", back_populates="user", lazy=True)


    manager_projects = db.relationship('Project', back_populates='manager_user', foreign_keys='Project.manager_id', lazy=True)
    created_projects = db.relationship('Project', back_populates='created_by_user', foreign_keys='Project.created_by', lazy=True)
    updated_projects = db.relationship('Project', back_populates='updated_by_user', foreign_keys='Project.updated_by', lazy=True)

    # Get a user's manager
    # user = User.query.get(5)
    # print(user.manager.full_name)

    # # Get all subordinates of a manager
    # manager = User.query.get(2)
    # for subordinate in manager.subordinates:
    #     print(subordinate.full_name)


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    users = db.relationship('User', back_populates='role', lazy=True)

    # org_user_roles = db.relationship('OrgUserRole', back_populates='user_role', lazy=True)


class UserProject(db.Model):
    __tablename__ = 'user_project'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)


# class TimeEntry(db.Model):
#     __tablename__ = 'time_entries'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column( db.Integer, db.ForeignKey('users.id'), nullable=False )

#     # Clock-in fields
#     clock_in = db.Column(db.DateTime, server_default=func.now(), nullable=False,)
#     clock_in_lat = db.Column(db.Float)
#     clock_in_lng = db.Column(db.Float)

#     # Clock-out fields
#     clock_out = db.Column(db.DateTime)
#     clock_out_lat = db.Column(db.Float)
#     clock_out_lng = db.Column(db.Float)

#     is_regularized = db.Column(db.Boolean, default=False)
#     regularized_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Admin ID
#     regularized_at = db.Column(db.DateTime)
#     regularization_reason = db.Column(db.Text)

