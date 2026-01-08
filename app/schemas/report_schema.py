
from marshmallow import Schema, fields

class ProjectReportSchema(Schema):
    user_codes = fields.List(fields.Str(), required=False)
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)