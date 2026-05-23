from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Category, Product
from app.routes.users import admin_required

products_bp = Blueprint('products', __name__,
                        template_folder='../templates')

SORT_OPTIONS = {
    'id': Product.id,
    'name': Product.name,
    'price': Product.price,
    'quantity': Product.quantity,
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

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter(Product.category_id == category_id)

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
                           categories=categories)


@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
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
            db.session.add(product)
            db.session.commit()
            flash('Thêm sản phẩm thành công!', 'success')
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=None,
                           categories=categories)


@products_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
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
            db.session.commit()
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=product,
                           categories=categories)


@products_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    product = db.get_or_404(Product, id)
    db.session.delete(product)
    db.session.commit()
    flash('Xóa sản phẩm thành công!', 'success')
    return redirect(url_for('products.list'))
