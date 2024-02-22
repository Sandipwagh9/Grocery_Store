from flask_sqlalchemy import SQLAlchemy
from datetime import date
from passlib.hash import pbkdf2_sha256 as passhash
from application.database import db


class Section(db.Model):
    __tablename__ = 'section'
    Category_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Category_name=db.Column(db.String,nullable=False)


class User(db.Model):
    User_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_name = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)

    cart = db.relationship('User_Cart', uselist=False, back_populates="user", cascade="all, delete-orphan")

    def __init__(self, User_name, Password):
        self.User_name = User_name
        self.Password = passhash.hash(Password)
        self.Cart = User_Cart()

    def __repr__(self):
        return f'<User {self.User_name}>'


class Manager(db.Model):
    Manager_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Manager_name=db.Column(db.String,nullable=False)
    Password=db.Column(db.String,nullable=False)

    def __init__(self, Manager_name, Password):
        self.Manager_name = Manager_name
        self.Password = passhash.hash(Password)

class Product(db.Model):
    __tablename__ = 'product'
    Product_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    Product_name=db.Column(db.String,nullable=False)
    Rate_per_unit=db.Column(db.Integer,nullable=False)
    Stock=db.Column(db.Integer,nullable=False)
    Expiry_date=db.Column(db.String,nullable=False)
    Image_url = db.Column(db.String)
    Category_id = db.Column(db.Integer, db.ForeignKey('section.Category_id'))
    quantity=db.Column(db.Integer,nullable=False,default=1)
    section = db.relationship('Section', backref = db.backref('products',lazy=True))
    Manager_id = db.Column(db.Integer, db.ForeignKey('manager.Manager_id'))
    Manager = db.relationship('Manager', backref = db.backref('products',lazy=True))


    

ucp=db.Table("ucp",
             db.Column("User_id",db.Integer, db.ForeignKey("user.User_id"),primary_key=True),
             db.Column("Product_id",db.Integer, db.ForeignKey("product.Product_id"),primary_key=True),
             db.Column("quantity",db.Integer,nullable=False,default=1)
             )

class User_Cart(db.Model):
    cart_id=db.Column(db.Integer,primary_key=True)
    User_id=db.Column(db.Integer,db.ForeignKey("user.User_id"))

    user=db.relationship("User",back_populates="cart")
    Cart_products=db.relationship("Product",secondary=ucp,lazy="subquery",
                                  backref=db.backref("carts",lazy=True),
                                  primaryjoin="User_Cart.cart_id==ucp.c.User_id",
                                  secondaryjoin="Product.Product_id==ucp.c.Product_id")
    def __repr__(self):
        return f'User_Cart {self.cart_id}'