def test_category_list_empty(client):
    resp = client.get('/categories')
    assert resp.status_code == 200
    assert 'Chưa có nh'.encode() in resp.data


def test_category_create(client):
    resp = client.post('/categories/add', data={
        'name': 'Điện thoại',
        'description': 'Các loại điện thoại',
    })
    assert resp.status_code == 302
    assert resp.location.endswith('/categories')

    resp = client.get('/categories')
    assert resp.status_code == 200
    assert 'Điện thoại'.encode() in resp.data


def test_category_edit(client):
    client.post('/categories/add', data={'name': 'Old Name'})
    resp = client.post('/categories/edit/1', data={
        'name': 'New Name',
        'description': 'Updated',
    })
    assert resp.status_code == 302

    resp = client.get('/categories')
    assert b'New Name' in resp.data
    assert b'Old Name' not in resp.data


def test_category_delete(client):
    client.post('/categories/add', data={'name': 'To Delete'})
    resp = client.post('/categories/delete/1')
    assert resp.status_code == 302

    resp = client.get('/categories')
    assert b'To Delete' not in resp.data
