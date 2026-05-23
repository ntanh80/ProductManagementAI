# ProductManagementAI

Web application quản lý Nhóm sản phẩm (Category) và Sản phẩm (Product) xây dựng bằng Flask.

## Công nghệ

- **Python** / **Flask** — Web framework
- **SQLAlchemy** — ORM
- **SQLite** — Cơ sở dữ liệu
- **Bootstrap 5** — Giao diện

## Cấu trúc thư mục

```
ProductManagementAI/
├── run.py                 # Entry point
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── config.py          # Cấu hình (dev/test/prod)
│   ├── extensions.py      # db instance
│   ├── models/            # SQLAlchemy models (Category, Product)
│   ├── routes/            # Blueprints (categories, products)
│   ├── templates/         # Bootstrap HTML
│   └── static/
├── tests/                 # Pytest
├── migrations/
└── instance/              # SQLite DB (tự động tạo)
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
pip install flask flask-sqlalchemy

# 3. Chạy
python run.py
```

Mở trình duyệt tại `http://127.0.0.1:5000`

## Chạy test

```powershell
pip install pytest
pytest
```

## Chức năng

### Nhóm sản phẩm (Category)
- Danh sách, Thêm, Sửa, Xóa
- Xóa nhóm sẽ xóa toàn bộ sản phẩm trong nhóm

### Sản phẩm (Product)
- Danh sách, Thêm, Sửa, Xóa
- Chọn nhóm sản phẩm khi thêm/sửa
