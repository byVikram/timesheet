from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    full_name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    org_code = fields.Str()
    role_code = fields.Str(required=True)

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True)
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class GetUsersSchema(Schema):
    page=fields.Integer()
    per_page=fields.Integer()


class UserCodeSchema(Schema):
    user_code = fields.Str()

class UserResponseSchema(Schema):
    user_code = fields.Str()
    username = fields.Str()
    email = fields.Email()
    full_name = fields.Str()

class AssignProjectSchema(Schema):
    user_code = fields.Str(required=True)
    project_code = fields.Str(required=True)