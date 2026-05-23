from datetime import datetime
from functools import wraps
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Category, Product, StockTransaction
from app.permissions import PERMISSION_DEFINITIONS
from app.utils import log_activity, export_workbook

users_bp = Blueprint('users', __name__, template_folder='../templates')


def permission_required(*perms):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vui lòng đăng nhập để tiếp tục.', 'info')
                return redirect(url_for('auth.login'))
            for perm in perms:
                if not current_user.has_permission(perm):
                    flash('Bạn không có quyền thực hiện thao tác này.', 'danger')
                    return redirect(url_for('products.list'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_permission('users.view'):
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('products.list'))
        return f(*args, **kwargs)
    return decorated


@users_bp.route('/')
@login_required
@admin_required
def dashboard():
    from datetime import timedelta

    total_value = db.session.query(
        func.sum(Product.price * Product.quantity)
    ).scalar() or 0

    categories = Category.query.all()
    chart_labels = [c.name for c in categories]
    chart_counts = [len(c.products) for c in categories]

    # Category stock value (doughnut chart)
    category_values = []
    for c in categories:
        val = db.session.query(
            func.sum(Product.price * Product.quantity)
        ).filter(Product.category_id == c.id).scalar() or 0
        category_values.append(val)

    top_products = Product.query.order_by(Product.quantity.desc()).limit(5).all()
    top_by_value = Product.query.order_by(
        (Product.price * Product.quantity).desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.quantity < 10).count()
    total_users = User.query.count()
    active_users = User.query.filter(User.is_active == True).count()

    # Recent stock movements
    recent_stock = StockTransaction.query.order_by(
        StockTransaction.created_at.desc()).limit(5).all()

    # User registrations last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_users = User.query.filter(
        User.created_at >= thirty_days_ago).count() if hasattr(User, 'created_at') else 0

    # Registration chart data (last 7 days)
    reg_labels = []
    reg_counts = []
    if hasattr(User, 'created_at'):
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime('%d/%m')
            reg_labels.append(day)
            day_start = datetime.now() - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            count = User.query.filter(
                User.created_at >= day_start,
                User.created_at < day_end,
            ).count()
            reg_counts.append(count)

    return render_template('dashboard.html',
                           now=datetime.now().strftime('%d/%m/%Y %H:%M'),
                           total_products=Product.query.count(),
                           total_categories=len(categories),
                           total_users=total_users,
                           active_users=active_users,
                           total_value=total_value,
                           chart_labels=chart_labels,
                           chart_counts=chart_counts,
                           category_values=category_values,
                           top_products=top_products,
                           top_by_value=top_by_value,
                           recent_products=recent_products,
                           recent_stock=recent_stock,
                           low_stock=low_stock,
                           new_users=new_users,
                           reg_labels=reg_labels,
                           reg_counts=reg_counts)


SORT_OPTIONS_USERS = {
    'id': User.id,
    'username': User.username,
    'full_name': User.full_name,
    'email': User.email,
    'role': User.role,
    'is_active': User.is_active,
    'created_at': User.created_at,
    'last_login': User.last_login,
}


@users_bp.route('/users')
@login_required
@admin_required
def list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'username')
    order = request.args.get('order', 'asc')
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')

    query = User.query

    if search:
        query = query.filter(
            db.or_(User.username.ilike(f'%{search}%'),
                   User.full_name.ilike(f'%{search}%'),
                   User.email.ilike(f'%{search}%'))
        )
    if role_filter:
        query = query.filter(User.role == role_filter)
    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)

    sort_col = SORT_OPTIONS_USERS.get(sort, User.username)
    if order == 'desc':
        sort_col = sort_col.desc()

    pagination = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    total_users = User.query.count()
    active_users = User.query.filter(User.is_active == True).count()
    admin_count = User.query.filter(User.role == 'admin').count()

    filter_kwargs = {}
    if search:
        filter_kwargs['search'] = search
    if role_filter:
        filter_kwargs['role'] = role_filter
    if status_filter:
        filter_kwargs['status'] = status_filter

    return render_template('users/list.html', pagination=pagination,
                           sort=sort, order=order, per_page=per_page,
                           search=search, role_filter=role_filter,
                           status_filter=status_filter,
                           filter_kwargs=filter_kwargs,
                           total_users=total_users, active_users=active_users,
                           admin_count=admin_count)


@users_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            from app.permissions import get_default_permissions
            user = User(username=username, full_name=full_name, email=email,
                        phone=phone, role=role,
                        permissions=__import__('json').dumps(
                            get_default_permissions(role), ensure_ascii=False))
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            log_activity('create', 'user', user.id,
                         {'username': username, 'role': role})
            flash('Thêm người dùng thành công!', 'success')
            return redirect(url_for('users.list'))

    return render_template('users/form.html', user=None)


@users_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = db.get_or_404(User, id)
    if request.method == 'POST':
        username = request.form['username'].strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'user')
        password = request.form.get('password', '')

        if not username:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif username != user.username and User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            user.username = username
            user.full_name = full_name
            user.email = email
            user.phone = phone
            if user.role != role:
                user.role = role
                from app.permissions import get_default_permissions
                import json
                user.permissions = json.dumps(
                    get_default_permissions(role), ensure_ascii=False)
            if password.strip():
                user.set_password(password.strip())
            db.session.commit()
            log_activity('edit', 'user', user.id,
                         {'username': username, 'role': role})
            flash('Cập nhật người dùng thành công!', 'success')
            return redirect(url_for('users.list'))

    return render_template('users/form.html', user=user)


@users_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    user = db.get_or_404(User, id)
    if user.id == current_user.id:
        flash('Bạn không thể tự xóa chính mình.', 'danger')
    else:
        log_activity('delete', 'user', id,
                     {'username': user.username})
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    return redirect(url_for('users.list'))


@users_bp.route('/users/export')
@login_required
@admin_required
def export_xlsx():
    users = User.query.order_by(User.username).all()
    headers = ['ID', 'Tên đăng nhập', 'Họ tên', 'Email', 'Số điện thoại',
               'Vai trò', 'Trạng thái', 'Lần đăng nhập cuối']
    rows = []
    for u in users:
        rows.append([
            u.id, u.username, u.full_name or '', u.email or '',
            u.phone or '',
            'Admin' if u.role == 'admin' else 'User',
            'Hoạt động' if u.is_active else 'Đã khóa',
            u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else '',
        ])
    return export_workbook(headers, rows, 'danh-sach-nguoi-dung')
