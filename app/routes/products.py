import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.extensions import db
from app.models import Category, Product
from app.routes.users import permission_required
from app.utils import log_activity, export_workbook
from datetime import datetime
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

products_bp = Blueprint('products', __name__,
                        template_folder='../templates')

SORT_OPTIONS = {
    'id': Product.id,
    'name': Product.name,
    'price': Product.price,
    'quantity': Product.quantity,
    'category': Category.name,
    'created_at': Product.created_at,
}


@products_bp.route('/products')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', 0, type=int)
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 0, type=float)
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    stock_status = request.args.get('stock_status', '').strip()

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price > 0:
        query = query.filter(Product.price >= min_price)
    if max_price > 0:
        query = query.filter(Product.price <= max_price)
    if date_from:
        try:
            dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Product.created_at >= dt)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(Product.created_at <= dt)
        except ValueError:
            pass
    if stock_status == 'in_stock':
        query = query.filter(Product.quantity > 10)
    elif stock_status == 'low_stock':
        query = query.filter(Product.quantity >= 1,
                             Product.quantity <= 10)
    elif stock_status == 'out_of_stock':
        query = query.filter(Product.quantity == 0)
    if sort == 'category':
        query = query.join(Product.category)

    sort_col = SORT_OPTIONS.get(sort, Product.name)
    if order == 'desc':
        sort_col = sort_col.desc()

    pagination = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.order_by(Category.name).all()

    return render_template('products/list.html', pagination=pagination,
                           sort=sort, order=order, per_page=per_page,
                           search=search, category_id=category_id,
                           categories=categories,
                           min_price=min_price, max_price=max_price,
                           date_from=date_from, date_to=date_to,
                           stock_status=stock_status)


@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@permission_required('products.create')
def add():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form.get('price', 0)
        quantity = request.form.get('quantity', 0)
        cat_id = request.form.get('category_id')
        if not name or not cat_id:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        else:
            product = Product(
                name=name, price=float(price), quantity=int(quantity),
                category_id=int(cat_id),
            )
            # Handle image upload
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
                filename = f'product_{product.id}_{product.name[:30].strip()}.{ext}'
                upload_dir = os.path.join(
                    current_app.root_path, '..', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                product.image = filename

            db.session.add(product)
            db.session.commit()

            # If image was saved before commit, re-save with correct ID
            if file and file.filename and allowed_file(file.filename):
                old_path = os.path.join(upload_dir, filename)
                new_filename = f'product_{product.id}.{ext}'
                new_path = os.path.join(upload_dir, new_filename)
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                product.image = new_filename
                db.session.commit()

            log_activity('create', 'product', product.id,
                         {'name': name, 'price': price, 'quantity': quantity})
            flash('Thêm sản phẩm thành công!', 'success')
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=None,
                           categories=categories)


@products_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('products.edit')
def edit(id):
    product = db.get_or_404(Product, id)
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form.get('price', 0)
        quantity = request.form.get('quantity', 0)
        cat_id = request.form.get('category_id')
        if not name or not cat_id:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        else:
            product.name = name
            product.price = float(price)
            product.quantity = int(quantity)
            product.category_id = int(cat_id)

            # Handle image upload
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
                filename = f'product_{product.id}.{ext}'
                upload_dir = os.path.join(
                    current_app.root_path, '..', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                # Delete old image
                if product.image:
                    old_path = os.path.join(upload_dir, product.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                file.save(os.path.join(upload_dir, filename))
                product.image = filename
            elif request.form.get('remove_image'):
                upload_dir = os.path.join(
                    current_app.root_path, '..', 'static', 'uploads')
                if product.image:
                    old_path = os.path.join(upload_dir, product.image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                product.image = None

            db.session.commit()
            log_activity('edit', 'product', product.id,
                         {'name': name, 'price': price, 'quantity': quantity})
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=product,
                           categories=categories)


@products_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('products.delete')
def delete(id):
    product = db.get_or_404(Product, id)
    # Delete image file if exists
    if product.image:
        upload_dir = os.path.join(
            current_app.root_path, '..', 'static', 'uploads')
        img_path = os.path.join(upload_dir, product.image)
        if os.path.exists(img_path):
            os.remove(img_path)
    log_activity('delete', 'product', id, {'name': product.name})
    db.session.delete(product)
    db.session.commit()
    flash('Xóa sản phẩm thành công!', 'success')
    return redirect(url_for('products.list'))


@products_bp.route('/products/export')
@login_required
def export_xlsx():
    query = Product.query.join(Product.category).order_by(Product.name)
    products = query.all()
    headers = ['ID', 'Tên sản phẩm', 'Giá', 'Số lượng', 'Nhóm sản phẩm',
               'Ngày tạo']
    rows = []
    for p in products:
        rows.append([
            p.id, p.name, p.price, p.quantity, p.category.name,
            p.created_at.strftime('%d/%m/%Y') if p.created_at else '',
        ])
    return export_workbook(headers, rows, 'danh-sach-san-pham')
