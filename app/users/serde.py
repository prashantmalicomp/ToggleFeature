from flask_marshmallow import Marshmallow
from marshmallow import fields, pre_load
from app.models import User

ma = Marshmallow()


class UserMinSchema(ma.Schema):
    id = fields.Integer()
    email = fields.String()
    username = fields.String()
    role = fields.String()



class UserSchema(ma.SQLAlchemyAutoSchema):

    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=True)

    class Meta:
        model = User
        include_fk = True