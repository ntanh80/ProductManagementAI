from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Category
from app.routes.users import admin_required

categories_bp = Blueprint('categories', __name__,
                          template_folder='../templates')

SORT_OPTIONS = {
    'id': Category.id,
    'name': Category.name,
    'description': Category.description,
}


@categories_bp.route('/categories')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    per_page = request.args.get('per_page', 10, type=int)

    sort_col = SORT_OPTIONS.get(sort, Category.name)
    if order == 'desc':
        sort_col = sort_col.desc()

    pagination = Category.query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('categories/list.html', pagination=pagination,
                           sort=sort, order=order, per_page=per_page)


@categories_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            flash('Thêm nhóm sản phẩm thành công!', 'success')
            return redirect(url_for('categories.list'))
        flash('Vui lòng nhập tên nhóm.', 'danger')
    return render_template('categories/form.html', category=None)


@categories_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    category = db.get_or_404(Category, id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category.name = name
            category.description = description
            db.session.commit()
            flash('Cập nhật nhóm sản phẩm thành công!', 'success')
            return redirect(url_for('categories.list'))
        flash('Vui lòng nhập tên nhóm.', 'danger')
    return render_template('categories/form.html', category=category)


@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    category = db.get_or_404(Category, id)
    db.session.delete(category)
    db.session.commit()
    flash('Xóa nhóm sản phẩm thành công!', 'success')
    return redirect(url_for('categories.list'))
