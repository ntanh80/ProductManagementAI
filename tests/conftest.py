import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        if User.query.count() == 0:
            admin = User(username='admin', full_name='Admin', role='admin')
            admin.set_password('admin')
            _db.session.add(admin)
            _db.session.commit()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture
def login_admin(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin',
    })
    return client
