from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Product, StockTransaction
from app.routes.users import permission_required
from app.utils import log_activity, export_workbook

inventory_bp = Blueprint('inventory', __name__, template_folder='../templates')


@inventory_bp.route('/inventory')
@login_required
@permission_required('inventory.view')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    type_filter = request.args.get('type', '')
    product_filter = request.args.get('product_id', 0, type=int)

    query = StockTransaction.query.order_by(
        StockTransaction.created_at.desc())

    if type_filter:
        query = query.filter(StockTransaction.type == type_filter)
    if product_filter:
        query = query.filter(StockTransaction.product_id == product_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = Product.query.order_by(Product.name).all()

    return render_template('inventory/list.html', pagination=pagination,
                           type_filter=type_filter,
                           product_filter=product_filter,
                           products=products)


@inventory_bp.route('/inventory/import', methods=['GET', 'POST'])
@login_required
@permission_required('inventory.import')
def import_stock():
    products = Product.query.order_by(Product.name).all()
    if request.method == 'POST':
        product_id = request.form.get('product_id', 0, type=int)
        quantity = request.form.get('quantity', 0, type=int)
        reference = request.form.get('reference', '').strip()
        notes = request.form.get('notes', '').strip()

        product = db.session.get(Product, product_id)
        if not product:
            flash('Vui lòng chọn sản phẩm.', 'danger')
        elif quantity <= 0:
            flash('Số lượng phải lớn hơn 0.', 'danger')
        else:
            product.quantity += quantity
            txn = StockTransaction(
                product_id=product_id, type='import',
                quantity=quantity, reference=reference,
                notes=notes, created_by=current_user.id)
            db.session.add(txn)
            db.session.commit()
            log_activity('import', 'stock_transaction', txn.id,
                         {'product': product.name, 'quantity': quantity,
                          'reference': reference})
            flash(f'Nhập kho {product.name}: +{quantity}', 'success')
            return redirect(url_for('inventory.list'))

    return render_template('inventory/form.html', products=products,
                           transaction_type='import')


@inventory_bp.route('/inventory/export', methods=['GET', 'POST'])
@login_required
@permission_required('inventory.export')
def export_stock():
    products = Product.query.order_by(Product.name).all()
    if request.method == 'POST':
        product_id = request.form.get('product_id', 0, type=int)
        quantity = request.form.get('quantity', 0, type=int)
        reference = request.form.get('reference', '').strip()
        notes = request.form.get('notes', '').strip()

        product = db.session.get(Product, product_id)
        if not product:
            flash('Vui lòng chọn sản phẩm.', 'danger')
        elif quantity <= 0:
            flash('Số lượng phải lớn hơn 0.', 'danger')
        elif product.quantity < quantity:
            flash(f'Tồn kho không đủ (hiện có: {product.quantity}).',
                  'danger')
        else:
            product.quantity -= quantity
            txn = StockTransaction(
                product_id=product_id, type='export',
                quantity=quantity, reference=reference,
                notes=notes, created_by=current_user.id)
            db.session.add(txn)
            db.session.commit()
            log_activity('export', 'stock_transaction', txn.id,
                         {'product': product.name, 'quantity': quantity,
                          'reference': reference})
            flash(f'Xuất kho {product.name}: -{quantity}', 'success')
            return redirect(url_for('inventory.list'))

    return render_template('inventory/form.html', products=products,
                           transaction_type='export')


@inventory_bp.route('/inventory/product/<int:product_id>')
@login_required
@permission_required('inventory.view')
def product_history(product_id):
    product = db.get_or_404(Product, product_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = StockTransaction.query.filter_by(
        product_id=product_id).order_by(
        StockTransaction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('inventory/product_history.html',
                           product=product, pagination=pagination)


@inventory_bp.route('/inventory/export-xlsx')
@login_required
@permission_required('inventory.view')
def export_xlsx():
    type_filter = request.args.get('type', '')
    product_filter = request.args.get('product_id', 0, type=int)

    query = StockTransaction.query.order_by(
        StockTransaction.created_at.desc())
    if type_filter:
        query = query.filter(StockTransaction.type == type_filter)
    if product_filter:
        query = query.filter(StockTransaction.product_id == product_filter)

    transactions = query.all()
    headers = ['ID', 'Sản phẩm', 'Loại', 'Số lượng', 'Tham chiếu',
               'Ghi chú', 'Người tạo', 'Thời gian']
    rows = []
    for t in transactions:
        rows.append([
            t.id, t.product.name if t.product else 'N/A',
            'Nhập kho' if t.type == 'import' else 'Xuất kho',
            t.quantity, t.reference or '', t.notes or '',
            t.creator.username if t.creator else '',
            t.created_at.strftime('%d/%m/%Y %H:%M') if t.created_at else '',
        ])
    return export_workbook(headers, rows, 'lich-su-kho')
