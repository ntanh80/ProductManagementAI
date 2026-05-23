from flask import Flask
from app.config import config
from app.extensions import db


def create_app(config_name=None):
    if config_name is None:
        config_name = 'development'

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)

    from app.routes.categories import categories_bp
    from app.routes.products import products_bp

    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('products.list'))

    with app.app_context():
        from app.models import Category, Product  # noqa: F401
        db.create_all()

    return app
