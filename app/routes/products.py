from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from app.models import Category, Product

products_bp = Blueprint('products', __name__,
                        template_folder='../templates')


@products_bp.route('/products')
def list():
    products = Product.query.all()
    return render_template('products/list.html', products=products)


@products_bp.route('/products/add', methods=['GET', 'POST'])
def add():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form.get('price', 0)
        quantity = request.form.get('quantity', 0)
        category_id = request.form.get('category_id')
        if name and category_id:
            product = Product(
                name=name,
                price=float(price),
                quantity=int(quantity),
                category_id=int(category_id),
            )
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=None,
                           categories=categories)


@products_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    product = db.get_or_404(Product, id)
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name'].strip()
        price = request.form.get('price', 0)
        quantity = request.form.get('quantity', 0)
        category_id = request.form.get('category_id')
        if name and category_id:
            product.name = name
            product.price = float(price)
            product.quantity = int(quantity)
            product.category_id = int(category_id)
            db.session.commit()
            return redirect(url_for('products.list'))
    return render_template('products/form.html', product=product,
                           categories=categories)


@products_bp.route('/products/delete/<int:id>', methods=['POST'])
def delete(id):
    product = db.get_or_404(Product, id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products.list'))
