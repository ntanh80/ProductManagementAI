from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import AuditLog
from app.routes.users import permission_required

audit_bp = Blueprint('audit', __name__, template_folder='../templates')


@audit_bp.route('/audit-log')
@login_required
@permission_required('audit.view')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action_filter = request.args.get('action', '')
    entity_filter = request.args.get('entity_type', '')

    query = AuditLog.query.order_by(AuditLog.timestamp.desc())

    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    if entity_filter:
        query = query.filter(AuditLog.entity_type == entity_filter)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    actions = ['create', 'edit', 'delete', 'import', 'export', 'login',
               'logout']
    entity_types = ['product', 'category', 'user', 'stock_transaction']

    return render_template('audit_log/list.html', pagination=pagination,
                           action_filter=action_filter,
                           entity_filter=entity_filter,
                           actions=actions, entity_types=entity_types)
