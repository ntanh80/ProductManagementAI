from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import or_
from app.extensions import db
from app.models import Category
from app.routes.users import permission_required
from app.utils import log_activity

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
    q = request.args.get('q', '').strip()

    sort_col = SORT_OPTIONS.get(sort, Category.name)
    if order == 'desc':
        sort_col = sort_col.desc()

    query = Category.query
    if q:
        query = query.filter(
            or_(
                Category.name.ilike(f'%{q}%'),
                Category.description.ilike(f'%{q}%'),
            )
        )

    pagination = query.order_by(sort_col).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('categories/list.html', pagination=pagination,
                           sort=sort, order=order, per_page=per_page, q=q)


@categories_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@permission_required('categories.create')
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            log_activity('create', 'category', category.id,
                         {'name': name})
            flash('Thêm nhóm sản phẩm thành công!', 'success')
            return redirect(url_for('categories.list'))
        flash('Vui lòng nhập tên nhóm.', 'danger')
    return render_template('categories/form.html', category=None)


@categories_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('categories.edit')
def edit(id):
    category = db.get_or_404(Category, id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category.name = name
            category.description = description
            db.session.commit()
            log_activity('edit', 'category', category.id,
                         {'name': name})
            flash('Cập nhật nhóm sản phẩm thành công!', 'success')
            return redirect(url_for('categories.list'))
        flash('Vui lòng nhập tên nhóm.', 'danger')
    return render_template('categories/form.html', category=category)


@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
@permission_required('categories.delete')
def delete(id):
    category = db.get_or_404(Category, id)
    log_activity('delete', 'category', id, {'name': category.name})
    db.session.delete(category)
    db.session.commit()
    flash('Xóa nhóm sản phẩm thành công!', 'success')
    return redirect(url_for('categories.list'))
