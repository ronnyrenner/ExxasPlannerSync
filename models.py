from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exxas_api_url = db.Column(db.String(256))
    exxas_api_key = db.Column(db.String(256))
    ms_tenant_id = db.Column(db.String(256))
    ms_client_id = db.Column(db.String(256))
    ms_client_secret = db.Column(db.String(256))
    sync_interval = db.Column(db.Integer, default=60)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class SyncLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))
    message = db.Column(db.Text)
    details = db.Column(db.Text)
