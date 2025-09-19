# From blueprint:python_log_in_with_replit integration
from datetime import datetime

from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

# Additional models for CoreAssist connector credentials
class ConnectorCredential(db.Model):
    __tablename__ = 'connector_credentials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    connector_name = db.Column(db.String, nullable=False)
    credentials_data = db.Column(db.Text, nullable=False)  # JSON encrypted credentials
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = db.relationship(User, backref='connector_credentials')
    
    __table_args__ = (UniqueConstraint(
        'user_id',
        'connector_name',
        name='uq_user_connector',
    ),)

# User API tokens for FastAPI authentication
class UserToken(db.Model):
    __tablename__ = 'user_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), nullable=False)
    token_hash = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)  # Human-readable name for the token
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_used = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship(User, backref='api_tokens')