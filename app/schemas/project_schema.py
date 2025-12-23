
from marshmallow import Schema, fields, validate

class ProjectDetailsSchema(Schema):
    project_code = fields.Str(required=True)

class ProjectCreationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str()
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    manager_code = fields.Str()

class TaskCreationSchema(Schema):
    project_code = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str()


class GetTasksSchema(Schema):
    project_code = fields.Str(required=True)


class UserResponseSchema(Schema):
    user_code = fields.Str()
    username = fields.Str()
    email = fields.Email()
    full_name = fields.Str()
