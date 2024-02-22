from applications.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Purchases(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.Date, nullable=False, default=date.today)