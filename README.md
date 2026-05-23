# ProductManagementAI

Web application quản lý sản phẩm, kho hàng và nhóm sản phẩm xây dựng bằng Flask, với phân quyền chi tiết và hỗ trợ đăng nhập bằng Google.

## Công nghệ

- **Python** / **Flask** 3.x — Web framework
- **SQLAlchemy** 3.x — ORM
- **Flask-Login** — Xác thực người dùng
- **SQLite** — Cơ sở dữ liệu
- **Bootstrap 5** + **SB Admin 2** — Giao diện admin
- **Chart.js** — Biểu đồ Dashboard
- **Authlib** — Google OAuth 2.0
- **pytest** — Kiểm thử

## Cấu trúc thư mục

```
ProductManagementAI/
├── app/
│   ├── __init__.py            # Flask app factory + migration
│   ├── config.py              # Cấu hình (dev/test/prod)
│   ├── extensions.py          # db, login_manager instances
│   ├── oauth.py               # Google OAuth setup
│   ├── permissions.py         # Định nghĩa quyền
│   ├── utils.py               # Audit log, export Excel
│   ├── models/
│   │   ├── user.py            # User (username, email, google_id, permissions...)
│   │   ├── product.py         # Product (name, price, quantity, timestamps)
│   │   ├── category.py        # Category
│   │   ├── audit_log.py       # AuditLog (action, entity, details)
│   │   └── stock_transaction.py  # StockTransaction (import/export)
│   ├── routes/
│   │   ├── auth.py            # Login, Register, Google OAuth, Profile
│   │   ├── users.py           # Dashboard, User CRUD + Export
│   │   ├── products.py        # Product CRUD + Advanced Search + Export
│   │   ├── categories.py      # Category CRUD
│   │   ├── audit_log.py       # Audit log viewer
│   │   └── inventory.py       # Stock import/export + history
│   └── templates/
│       ├── base.html          # SB Admin 2 layout
│       ├── _pagination.html   # Pagination macros
│       ├── auth/              # Login, Register, Profile, Change Password
│       ├── users/             # User list + form (admin)
│       ├── products/          # Product list + form
│       ├── categories/        # Category list + form
│       ├── inventory/         # Stock list, form, product history
│       ├── audit_log/         # Audit log viewer
│       └── emails/            # Email templates (verify, reset)
├── tests/                     # 33 pytest tests
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_products.py
│   ├── test_inventory.py
│   ├── test_audit_log.py
│   ├── test_permissions.py
│   ├── test_exports.py
│   └── conftest.py
├── seed.py                    # Seed database
├── requirements.txt
├── .env.example
└── README.md
```

## Yêu cầu

- Python >= 3.10
- pip

## Cài đặt & Chạy

```powershell
# 1. Clone repo
git clone https://github.com/ntanh80/ProductManagementAI.git
cd ProductManagementAI

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Chạy (development)
python -m flask run --debug

# Hoặc dùng seed data (47 sản phẩm, 10 danh mục, users)
python seed.py
python -m flask run --debug
```

Mở trình duyệt tại `http://127.0.0.1:5000`

## Tài khoản mặc định

| Tài khoản | Mật khẩu | Vai trò |
|-----------|----------|---------|
| `admin` | `admin` | Quản trị viên (toàn quyền) |
| `nguyenvanan` | `123456` | Người dùng (xem sản phẩm, dashboard) |

## Google OAuth

Cho phép đăng nhập bằng tài khoản Google. Cấu hình qua biến môi trường:

```powershell
# Tạo Google OAuth Client ID tại https://console.cloud.google.com/apis/credentials
$env:GOOGLE_CLIENT_ID = "xxx.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "GOCSPX-xxx"

# Redirect URI cần khai báo trong Google Console:
# http://localhost:5000/login/google/callback
```

Khi chưa cấu hình, nút "Đăng nhập bằng Google" ẩn đi, ứng dụng chạy bình thường.

## Chức năng

### Xác thực & Phân quyền
- Đăng nhập bằng username hoặc email
- Đăng nhập bằng Google (OAuth 2.0)
- Đăng ký tài khoản mới
- Đổi mật khẩu
- Hồ sơ cá nhân
- Hệ thống phân quyền chi tiết với 18 quyền

### Quản lý sản phẩm
- Danh sách, Thêm, Sửa, Xóa sản phẩm
- Tìm kiếm nâng cao: theo tên, nhóm, khoảng giá, ngày tạo, tình trạng tồn kho
- Sắp xếp theo mọi cột
- Xuất danh sách ra Excel

### Quản lý nhóm sản phẩm
- Danh sách, Thêm, Sửa, Xóa nhóm
- Xóa nhóm sẽ xóa toàn bộ sản phẩm trong nhóm

### Quản lý kho hàng
- Nhập kho / Xuất kho
- Kiểm tra tồn kho trước khi xuất
- Lịch sử giao dịch theo sản phẩm
- Lọc theo loại giao dịch, sản phẩm
- Xuất lịch sử ra Excel

### Quản lý người dùng (Admin)
- Danh sách, Thêm, Sửa, Xóa người dùng
- Gán vai trò (admin/user)
- Phân quyền chi tiết
- Thống kê (tổng, đang hoạt động, admin, đã khóa)
- Xuất danh sách ra Excel

### Nhật ký hoạt động
- Ghi lại mọi thao tác CRUD
- Ghi lại đăng nhập, xuất/nhập kho
- Lọc theo hành động, đối tượng

### Dashboard
- Thống kê tổng quan (sản phẩm, nhóm, người dùng, giá trị kho)
- Biểu đồ sản phẩm theo nhóm
- Biểu đồ tròn giá trị kho theo nhóm
- Top 5 sản phẩm giá trị nhất
- Giao dịch kho gần đây
- Biểu đồ người dùng mới (7 ngày)
- Cảnh báo tồn kho thấp

## Chạy test

```powershell
pytest
```

33 tests bao gồm: auth, categories, products, inventory, permissions, audit log, exports.

## Biến môi trường

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `SECRET_KEY` | Secret key cho session | `dev-secret-key` |
| `DATABASE_URL` | Đường dẫn database | `sqlite:///product_management.db` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | — |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | — |
