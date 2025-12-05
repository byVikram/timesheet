from marshmallow import Schema, fields, validate

class OrgRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)

class OrgLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class OrgResponseSchema(Schema):
    id = fields.Int()
    org_name = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()
