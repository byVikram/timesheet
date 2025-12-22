
from marshmallow import Schema, fields, validate

class ProjectReportSchema(Schema):
    user_codes = fields.List(fields.Str(), required=False)

