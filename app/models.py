import re
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class UserRoleEnum(Enum):
    ADMIN = 1
    MEMBER = 2


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True, index=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    role = db.Column(db.Unicode(255), server_default='member')
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('email')
    def validate_email(self, key, email):
        # Define a regular expression for a valid email address
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email:
            raise ValueError("Email address cannot be empty")
        if not re.match(pattern, email) is not None:
            raise ValueError("Invalid email address format")
        return email

    @validates('role')
    def validate_role(self, key, role):
        if role is not None:
            if role not in [u.name for u in UserRoleEnum]:
                raise ValueError("Invalid role : Role should be in 'ADMIN' or 'MEMBER'")
        return role


class ToggleStateEnum(Enum):
    ENABLE = 1
    DISABLE = 0


class EnvironmentEnum(Enum):
    DEV = 1
    QA = 2
    PROD = 3
    PERFQA = 4
    UAT = 5


# Define SQLAlchemy model for Feature Toggles
class FeatureToggle(db.Model):
    __tablename__ = 'toggle'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(200))
    state = db.Column(db.Boolean, default=False)
    environment = db.Column(db.String(255), nullable=False, server_default='Dev')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    updated_by = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    sb_id = db.Column(db.Integer(), nullable=True)
    version = db.Column(db.Integer(), nullable=False, default=1)
    status = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_user = db.relationship('User', backref='users_created', primaryjoin="User.id == FeatureToggle.created_by")
    updated_user = db.relationship('User', backref='users_updated', primaryjoin="User.id == FeatureToggle.updated_by")

    @validates('identifier')
    def validate_field(self, field, value):
        if not value:
            raise ValueError(f"{field} cannot be empty")
        return value

    def clone_model(model):
        """Clone FeatureToggle model object """
        table = model.__table__
        non_pk_columns = [k for k in table.columns.keys() if k not in table.primary_key.columns.keys()]
        data = {c: getattr(model, c) for c in non_pk_columns}
        clone = model.__class__(**data)
        db.session.add(clone)
        db.session.commit()
        return clone
