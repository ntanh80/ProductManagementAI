def test_inventory_list_requires_login(client):
    resp = client.get('/admin/inventory')
    assert resp.status_code == 302
    assert '/login' in resp.location


def test_import_stock(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Product A', 'price': 100, 'quantity': 5, 'category_id': 1,
    })
    resp = login_admin.post('/admin/inventory/import', data={
        'product_id': 1, 'quantity': 10, 'reference': 'PO-001',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert 'Nhập kho'.encode() in resp.data


def test_export_stock(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Product B', 'price': 100, 'quantity': 20, 'category_id': 1,
    })
    resp = login_admin.post('/admin/inventory/export', data={
        'product_id': 1, 'quantity': 5, 'reference': 'SO-001',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert 'Xuất kho'.encode() in resp.data


def test_export_insufficient_stock(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Product C', 'price': 100, 'quantity': 2, 'category_id': 1,
    })
    resp = login_admin.post('/admin/inventory/export', data={
        'product_id': 1, 'quantity': 99,
    }, follow_redirects=True)
    assert 'không đủ'.encode() in resp.data


def test_inventory_list_shows_transactions(login_admin):
    login_admin.post('/admin/categories/add', data={'name': 'DM'})
    login_admin.post('/admin/products/add', data={
        'name': 'Product D', 'price': 100, 'quantity': 5, 'category_id': 1,
    })
    login_admin.post('/admin/inventory/import', data={
        'product_id': 1, 'quantity': 10,
    })
    resp = login_admin.get('/admin/inventory')
    assert resp.status_code == 200
