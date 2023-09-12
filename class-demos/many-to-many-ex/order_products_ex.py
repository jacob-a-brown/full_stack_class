from flask import Flask
from flask_sqlalchemy import SQLAlchemy

p = inpurt('password please: ')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://brown:{p}@localhost:5432/example'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# table to set the many-to-many relation between Order and Product 
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Order(db.Model):
    """
    Parents of Product
    """

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)
    products = db.relationship('Product', secondary=order_items,
      backref=db.backref('orders', lazy=True))

class Product(db.Model):
    """
    Child of Order
    """


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')