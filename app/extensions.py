from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        return False


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.anonymous_user = AnonymousUser
