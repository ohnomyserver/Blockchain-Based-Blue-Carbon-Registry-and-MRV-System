from marshmallow import Schema, fields, validate, ValidationError

class UserRegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class CompanyRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    description = fields.Str(required=False, validate=validate.Length(max=255))

class CreditIssueSchema(Schema):
    company_id = fields.Int(required=True, validate=validate.Range(min=1))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=False, validate=validate.Length(max=255))

class CreditTransferSchema(Schema):
    receiver_id = fields.Int(required=True, validate=validate.Range(min=1))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
