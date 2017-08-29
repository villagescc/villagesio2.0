from marshmallow.schema import Schema
from marshmallow.validate import OneOf, Range
from marshmallow import fields

LISTING_TYPE = (('OF'),
                ('RQ'),
                ('TC'),
                ('LR'),
                ('GT'))


class SubmitListingSchema(Schema):

    listing_type = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String(required=False)
    price = fields.Decimal(required=True, default=0, validate=[Range(min=0, max=999)])
    subcategories = fields.Integer(required=True)
    tag = fields.String(required=False)
    id_photo = fields.String(required=False)
