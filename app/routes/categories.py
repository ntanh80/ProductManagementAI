from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from app.models import Category

categories_bp = Blueprint('categories', __name__,
                          template_folder='../templates')


@categories_bp.route('/categories')
def list():
    categories = Category.query.all()
    return render_template('categories/list.html', categories=categories)


@categories_bp.route('/categories/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('categories.list'))
    return render_template('categories/form.html', category=None)


@categories_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    category = db.get_or_404(Category, id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        if name:
            category.name = name
            category.description = description
            db.session.commit()
            return redirect(url_for('categories.list'))
    return render_template('categories/form.html', category=category)


@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
def delete(id):
    category = db.get_or_404(Category, id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('categories.list'))
