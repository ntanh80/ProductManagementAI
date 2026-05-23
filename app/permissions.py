PERMISSION_DEFINITIONS = {
    "products.view": "Xem sản phẩm",
    "products.create": "Thêm sản phẩm",
    "products.edit": "Sửa sản phẩm",
    "products.delete": "Xóa sản phẩm",
    "categories.view": "Xem nhóm sản phẩm",
    "categories.create": "Thêm nhóm sản phẩm",
    "categories.edit": "Sửa nhóm sản phẩm",
    "categories.delete": "Xóa nhóm sản phẩm",
    "users.view": "Xem người dùng",
    "users.create": "Thêm người dùng",
    "users.edit": "Sửa người dùng",
    "users.delete": "Xóa người dùng",
    "inventory.view": "Xem lịch sử kho",
    "inventory.import": "Nhập kho",
    "inventory.export": "Xuất kho",
    "audit.view": "Xem nhật ký hoạt động",
    "dashboard.view": "Xem Dashboard",
}

DEFAULT_PERMISSIONS = {
    "admin": set(PERMISSION_DEFINITIONS.keys()),
    "user": {"products.view", "categories.view", "dashboard.view"},
}


def get_default_permissions(role):
    return sorted(DEFAULT_PERMISSIONS.get(role, DEFAULT_PERMISSIONS["user"]))
