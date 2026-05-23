def test_export_products(login_admin):
    resp = login_admin.get('/admin/products/export')
    assert resp.status_code == 200
    assert resp.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'danh-sach-san-pham' in resp.headers.get('Content-Disposition', '')


def test_export_users(login_admin):
    resp = login_admin.get('/admin/users/export')
    assert resp.status_code == 200
    assert resp.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'danh-sach-nguoi-dung' in resp.headers.get('Content-Disposition', '')
