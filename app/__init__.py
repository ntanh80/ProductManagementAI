from flask import Flask
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

    app.register_blueprint(categories_bp, url_prefix='/admin')
    app.register_blueprint(products_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('users.dashboard'))

    with app.app_context():
        from app.models import User, Category, Product  # noqa: F401
        db.create_all()
        if User.query.count() == 0:
            admin = User(username='admin', full_name='Administrator',
                         role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
