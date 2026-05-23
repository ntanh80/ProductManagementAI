"""Seed 15 Vietnamese users."""
from app import create_app
from app.extensions import db
from app.models import User

users_data = [
    {"username": "admin", "password": "123456", "full_name": "Admin Hệ thống", "email": "admin@company.vn", "phone": "0901000001", "role": "admin", "is_active": True},
    {"username": "lan", "password": "123456", "full_name": "Nguyễn Thị Lan", "email": "lan.nguyen@company.vn", "phone": "0901000002", "role": "user", "is_active": True},
    {"username": "mai", "password": "123456", "full_name": "Trần Thị Mai", "email": "mai.tran@company.vn", "phone": "0901000003", "role": "user", "is_active": True},
    {"username": "hung", "password": "123456", "full_name": "Lê Văn Hùng", "email": "hung.le@company.vn", "phone": "0901000004", "role": "user", "is_active": True},
    {"username": "anh", "password": "123456", "full_name": "Phạm Văn Anh", "email": "anh.pham@company.vn", "phone": "0901000005", "role": "user", "is_active": True},
    {"username": "thao", "password": "123456", "full_name": "Hoàng Thị Thảo", "email": "thao.hoang@company.vn", "phone": "0901000006", "role": "user", "is_active": True},
    {"username": "long", "password": "123456", "full_name": "Vũ Đức Long", "email": "long.vu@company.vn", "phone": "0901000007", "role": "user", "is_active": True},
    {"username": "huong", "password": "123456", "full_name": "Đặng Thị Hương", "email": "huong.dang@company.vn", "phone": "0901000008", "role": "admin", "is_active": True},
    {"username": "tuan", "password": "123456", "full_name": "Bùi Văn Tuấn", "email": "tuan.bui@company.vn", "phone": "0901000009", "role": "user", "is_active": True},
    {"username": "linh", "password": "123456", "full_name": "Đỗ Thị Linh", "email": "linh.do@company.vn", "phone": "0901000010", "role": "user", "is_active": True},
    {"username": "ha", "password": "123456", "full_name": "Ngô Văn Hà", "email": "ha.ngo@company.vn", "phone": "0901000011", "role": "user", "is_active": False},
    {"username": "trang", "password": "123456", "full_name": "Cao Thị Trang", "email": "trang.cao@company.vn", "phone": "0901000012", "role": "user", "is_active": True},
    {"username": "duc", "password": "123456", "full_name": "Đinh Văn Đức", "email": "duc.dinh@company.vn", "phone": "0901000013", "role": "admin", "is_active": True},
    {"username": "quynh", "password": "123456", "full_name": "Phùng Thị Quỳnh", "email": "quynh.phung@company.vn", "phone": "0901000014", "role": "user", "is_active": True},
    {"username": "binh", "password": "123456", "full_name": "Trịnh Văn Bình", "email": "binh.trinh@company.vn", "phone": "0901000015", "role": "user", "is_active": False},
]

app = create_app()
with app.app_context():
    existing = User.query.count()
    added = 0
    for data in users_data:
        if User.query.filter_by(username=data["username"]).first():
            continue
        u = User(
            username=data["username"],
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            role=data["role"],
            is_active=data["is_active"],
        )
        u.set_password(data["password"])
        db.session.add(u)
        added += 1
    db.session.commit()
    total = User.query.count()
    print(f"Added {added} users. Total: {total}")
