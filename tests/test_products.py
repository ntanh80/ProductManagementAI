def test_product_list_requires_login(client):
    resp = client.get('/admin/products')
    assert resp.status_code == 302
    assert '/login' in resp.location


def test_product_list_empty(login_admin):
    resp = login_admin.get('/admin/products')
    assert resp.status_code == 200
    assert 'Chưa có sản phẩm'.encode() in resp.data


def test_product_create(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'Danh mục 1'})
    resp = login_admin.post('/admin/products/add', data={
        'name': 'Sản phẩm A',
        'price': 10000,
        'quantity': 5,
        'category_id': 1,
    })
    assert resp.status_code == 302

    resp = login_admin.get('/admin/products')
    assert 'Sản phẩm A'.encode() in resp.data


def test_product_edit(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Old Product', 'price': 100, 'quantity': 1, 'category_id': 1,
    })
    resp = login_admin.post('/admin/products/edit/1', data={
        'name': 'New Product', 'price': 200, 'quantity': 3, 'category_id': 1,
    })
    assert resp.status_code == 302

    resp = login_admin.get('/admin/products')
    assert b'New Product' in resp.data
    assert b'Old Product' not in resp.data


def test_product_delete(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'To Delete', 'price': 100, 'quantity': 1, 'category_id': 1,
    })
    resp = login_admin.post('/admin/products/delete/1')
    assert resp.status_code == 302

    resp = login_admin.get('/admin/products')
    assert b'To Delete' not in resp.data
