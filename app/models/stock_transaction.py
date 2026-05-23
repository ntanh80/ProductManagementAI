from datetime import datetime, timezone

from app.extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'import' or 'export'
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(200), default='')
    notes = db.Column(db.Text, default='')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    product = db.relationship('Product', backref=db.backref(
        'stock_transactions', lazy='dynamic', order_by='StockTransaction.created_at.desc()'))
    creator = db.relationship('User', backref=db.backref(
        'stock_transactions', lazy='dynamic'))

    def __repr__(self):
        return f'<StockTransaction {self.type} {self.quantity} of #{self.product_id}>'
