import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), default='')
    email = db.Column(db.String(120), default='')
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(20), default='')
    role = db.Column(db.String(20), nullable=False, default='user')
    permissions = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role

    def get_permissions(self):
        if self.permissions:
            return set(json.loads(self.permissions))
        from app.permissions import get_default_permissions
        return set(get_default_permissions(self.role))

    def has_permission(self, perm):
        return perm in self.get_permissions()

    def __repr__(self):
        return f'<User {self.username}>'
