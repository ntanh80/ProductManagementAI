from app.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')

    products = db.relationship('Product', backref='category', lazy=True,
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'
