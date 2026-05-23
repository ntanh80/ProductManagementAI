from datetime import datetime
from functools import wraps
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Category, Product

users_bp = Blueprint('users', __name__, template_folder='../templates')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role('admin'):
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('products.list'))
        return f(*args, **kwargs)
    return decorated


@users_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_value = db.session.query(
        func.sum(Product.price * Product.quantity)
    ).scalar() or 0

    categories = Category.query.all()
    chart_labels = [c.name for c in categories]
    chart_counts = [len(c.products) for c in categories]
    top_products = Product.query.order_by(Product.quantity.desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.quantity < 10).count()

    return render_template('dashboard.html',
                           now=datetime.now().strftime('%d/%m/%Y %H:%M'),
                           total_products=Product.query.count(),
                           total_categories=len(categories),
                           total_users=User.query.count(),
                           total_value=total_value,
                           chart_labels=chart_labels,
                           chart_counts=chart_counts,
                           top_products=top_products,
                           recent_products=recent_products,
                           low_stock=low_stock)


@users_bp.route('/users')
@login_required
@admin_required
def list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = User.query.order_by(User.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('users/list.html', pagination=pagination,
                           per_page=per_page)


@users_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            user = User(username=username, full_name=full_name, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
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
        role = request.form.get('role', 'user')
        password = request.form.get('password', '')

        if not username:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif username != user.username and User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            user.username = username
            user.full_name = full_name
            user.role = role
            if password.strip():
                user.set_password(password.strip())
            db.session.commit()
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
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    return redirect(url_for('users.list'))
