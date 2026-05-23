def test_login_page_loads(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'ng nh' in resp.data


def test_login_success(client):
    resp = client.post('/login', data={
        'username': 'admin',
        'password': 'admin',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'ng nh' in resp.data


def test_login_fail(client):
    resp = client.post('/login', data={
        'username': 'admin',
        'password': 'wrong',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Sai' in resp.data


def test_logout(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'ng nh' in resp.data


def test_register(client):
    resp = client.post('/register', data={
        'username': 'newuser',
        'password': 'pass123',
        'confirm': 'pass123',
        'full_name': 'New User',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'ng k' in resp.data


def test_register_duplicate(client):
    client.post('/register', data={
        'username': 'newuser', 'password': 'pass', 'confirm': 'pass',
    })
    resp = client.post('/register', data={
        'username': 'newuser', 'password': 'pass', 'confirm': 'pass',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert 'tồn tại'.encode() in resp.data


def test_user_cannot_access_admin(client):
    """Register a regular user and verify they cannot access user management."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    client.post('/users/add', data={
        'username': 'regular', 'password': 'pass', 'role': 'user',
    })

    client.get('/logout')
    client.post('/login', data={'username': 'regular', 'password': 'pass'})

    resp = client.get('/users', follow_redirects=True)
    assert 'không có quyền'.encode() in resp.data
