def test_permission_required_blocks(client):
    """Regular user cannot access admin-only features."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    client.post('/admin/users/add', data={
        'username': 'regular', 'password': 'pass', 'role': 'user',
    })
    client.get('/logout')
    client.post('/login', data={'username': 'regular', 'password': 'pass'})
    resp = client.post('/admin/categories/add', data={'name': 'Test'},
                       follow_redirects=True)
    assert 'không có quyền'.encode() in resp.data


def test_permission_granted_for_admin(client):
    """Admin user can access all features."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    resp = client.post('/admin/categories/add', data={'name': 'Test'},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert 'Thêm nhóm'.encode() in resp.data


def test_unauthenticated_redirect(client):
    """Unauthenticated users cannot access permission_required views."""
    resp = client.get('/admin/categories/add')
    assert resp.status_code == 302
    assert '/login' in resp.location
