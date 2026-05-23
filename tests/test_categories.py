def test_category_list_requires_login(client):
    resp = client.get('/admin/categories')
    assert resp.status_code == 302
    assert '/login' in resp.location


def test_category_list_empty(login_admin):
    resp = login_admin.get('/admin/categories')
    assert resp.status_code == 200
    assert 'Chưa có nhóm'.encode() in resp.data


def test_category_create(login_admin):
    resp = login_admin.post('/admin/categories/add', data={
        'name': 'Điện thoại',
        'description': 'Các loại điện thoại',
    })
    assert resp.status_code == 302

    resp = login_admin.get('/admin/categories')
    assert 'Điện thoại'.encode() in resp.data


def test_category_edit(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'Old Name'})
    resp = login_admin.post('/admin/categories/edit/1', data={
        'name': 'New Name',
        'description': 'Updated',
    })
    assert resp.status_code == 302

    resp = login_admin.get('/admin/categories')
    assert b'New Name' in resp.data
    assert b'Old Name' not in resp.data


def test_category_delete(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'To Delete'})
    resp = login_admin.post('/admin/categories/delete/1')
    assert resp.status_code == 302

    resp = login_admin.get('/admin/categories')
    assert b'To Delete' not in resp.data
