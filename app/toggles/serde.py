from marshmallow import fields
from flask_marshmallow import Marshmallow
from app.models import FeatureToggle
from app.users.serde import UserMinSchema

ma = Marshmallow()

# Define Marshmallow schema for Feature Toggle
class FeatureToggleSchema(ma.SQLAlchemyAutoSchema):
    identifier = fields.String()
    created_by = fields.Integer()
    created_user = fields.Nested(UserMinSchema())
    updated_user = fields.Nested(UserMinSchema())
    updated_by = fields.Integer()
    toggle_state = fields.Method('get_state')

    class Meta:
        model = FeatureToggle

    def get_state(self, model):
        model.toggle_state = "ENABLE" if model.state == 1 else "DISABLE"
        return model.toggle_state



