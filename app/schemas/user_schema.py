from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    # username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    # password = fields.Str(required=True, validate=validate.Length(min=6))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    org_code = fields.Str()
    is_active = fields.Bool()
    role = fields.Str(required=True)

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True)
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class GetUsersSchema(Schema):
    page=fields.Integer(load_default=1)
    per_page=fields.Integer(load_default=10)
    sort_by=fields.Str()
    sort_direction=fields.Str()
    variant=fields.Str()


class GetUserDetailsSchema(Schema):
    user_code=fields.Str(required=True)


class UserCodeSchema(Schema):
    user_code = fields.Str()

class UserResponseSchema(Schema):
    user_code = fields.Str()
    username = fields.Str()
    email = fields.Email()
    full_name = fields.Str()

class ManageUserProjectSchema(Schema):
    user_code = fields.Str(required=True)
    project_code = fields.Str(required=True)
    action = fields.Str(required=True)
    is_active=fields.Bool()