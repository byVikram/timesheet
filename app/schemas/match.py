from marshmallow import Schema, fields

class MatchSchema(Schema):
    id = fields.Int()
    team_a = fields.Str()
    team_b = fields.Str()
    match_date = fields.DateTime()
    venue = fields.Str()
