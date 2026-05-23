import os
import json
from flask import Flask
from dotenv import load_dotenv

# Load .env BEFORE config is imported
load_dotenv()

from app.config import config
from app.extensions import db, login_manager


def create_app(config_name=None):
    if config_name is None:
        config_name = 'development'

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'info'

    from app.routes.categories import categories_bp
    from app.routes.products import products_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.audit_log import audit_bp
    from app.routes.inventory import inventory_bp
    from app.routes.api import api_bp
    from app.oauth import init_oauth

    app.register_blueprint(categories_bp, url_prefix='/admin')
    app.register_blueprint(products_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp, url_prefix='/admin')
    app.register_blueprint(audit_bp, url_prefix='/admin')
    app.register_blueprint(inventory_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)

    init_oauth(app)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('users.dashboard'))

    @app.context_processor
    def inject_globals():
        from app.models import Product
        from app.translations import translate, get_language, SUPPORTED_LANGUAGES
        from flask_login import current_user
        low_stock_count = 0
        if current_user.is_authenticated:
            try:
                low_stock_count = Product.query.filter(
                    Product.quantity < 10).count()
            except Exception:
                pass
        lang = get_language()
        return dict(
            low_stock_count=low_stock_count,
            _=lambda t: translate(t, lang),
            current_lang=lang,
            supported_languages=SUPPORTED_LANGUAGES,
        )

    with app.app_context():
        from app.models import User, Category, Product, AuditLog, StockTransaction  # noqa: F401
        db.create_all()

        # Migrate existing tables
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)

        # Add permissions column to users if missing
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'permissions' not in user_cols:
            db.session.execute(text(
                'ALTER TABLE users ADD COLUMN permissions TEXT DEFAULT ""'))
            from app.permissions import get_default_permissions
            for user in User.query.all():
                if not user.permissions:
                    user.permissions = json.dumps(
                        list(get_default_permissions(user.role)),
                        ensure_ascii=False)
            db.session.commit()

        # Add google_id to users if missing
        if 'google_id' not in user_cols:
            db.session.execute(text(
                'ALTER TABLE users ADD COLUMN google_id VARCHAR(100)'))
            db.session.commit()

        # Add created_at/updated_at to products if missing
        prod_cols = [c['name'] for c in inspector.get_columns('products')]
        if 'created_at' not in prod_cols:
            from datetime import datetime, timezone
            db.session.execute(text(
                'ALTER TABLE products ADD COLUMN created_at TIMESTAMP'))
            db.session.execute(text(
                'ALTER TABLE products ADD COLUMN updated_at TIMESTAMP'))
            Product.query.update(
                {Product.created_at: datetime.now(timezone.utc)})
            db.session.commit()

        # Seed default admin if no users
        if User.query.count() == 0:
            from app.permissions import get_default_permissions
            admin = User(username='admin', full_name='Administrator',
                         role='admin',
                         permissions=json.dumps(
                             list(get_default_permissions('admin')),
                             ensure_ascii=False))
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
