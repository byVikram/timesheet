from marshmallow import Schema, fields

class SubscriptionKeysSchema(Schema):
    p256dh = fields.Str(required=True, metadata={"description": "Push subscription p256dh key"})
    auth = fields.Str(required=True, metadata={"description": "Push subscription auth key"})


class PushSubscriptionSchema(Schema):
    endpoint = fields.Str(required=True, metadata={"description": "Push subscription endpoint URL"})
    expirationTime = fields.Float(allow_none=True, metadata={"description": "Expiration timestamp or null"})
    keys = fields.Nested(SubscriptionKeysSchema, required=True)


class SubscriptionSchema(Schema):
    subscription = fields.Nested(PushSubscriptionSchema, required=True)
