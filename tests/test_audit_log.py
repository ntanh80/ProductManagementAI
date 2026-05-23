def test_audit_log_requires_permission(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    resp = client.get('/admin/audit-log')
    assert resp.status_code == 200


def test_audit_log_blocks_regular_user(client):
    """Regular users cannot access audit log."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    client.post('/admin/users/add', data={
        'username': 'regular', 'password': 'pass', 'role': 'user',
    })
    client.get('/logout')
    client.post('/login', data={'username': 'regular', 'password': 'pass'})
    resp = client.get('/admin/audit-log', follow_redirects=True)
    assert 'không có quyền'.encode() in resp.data


def test_audit_log_after_create_product(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Audit Test', 'price': 100, 'quantity': 5, 'category_id': 1,
    })
    resp = login_admin.get('/admin/audit-log')
    assert resp.status_code == 200
