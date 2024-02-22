from flask import render_template, request, session, redirect
from flask import current_app as app
from applications.database import db
from applications.models import User, Product, Purchases
from passlib.hash import pbkdf2_sha256 as passhash
import json

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        products = Product.query.all()
        if "user" in session:
            return render_template("home.html", user = session["user"], signed=True, products = products)
        else:
            return render_template("home.html", user = "", signed=False, products = products)
    else:
        product_id, count = request.form["product"], request.form["count"]
        product = Product.query.filter_by(id = product_id).first()
        
        cart = json.loads(session["cart"])
        if product_id in cart:
            current = int(count) + int(cart[product_id])
            if current <= int(product.stock):
                cart[product_id] = str(int(cart[product_id]) + int(count))
        else:
            current = int(count)
            if current <= int(product.stock):
                cart[product_id] = count

        session["cart"] = json.dumps(cart)
        print(session["cart"])
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password = passhash.hash(password)
        user = User.query.filter_by(name = username).first()        
        if user is not None:
            return redirect("/login")
        user = User(name = username, password = password)
        db.session.add(user)
        db.session.commit()
        session["user"] = username
        session["cart"] = json.dumps(dict())
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(name = username).first()
        if user is None:
            return redirect("/register")
        if not passhash.verify(password, user.password):
            return redirect("/login")
        session["user"] = username
        session["cart"] = json.dumps(dict())
        return redirect("/")

@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
        session.pop("cart")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.admin:
            products = Product.query.all()
            return render_template("admin_dashboard.html", products = products)
    return redirect("/")

@app.route("/add_product", methods = ["GET", "POST"])
def add_product():
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.admin:
            if request.method == "GET":
                return render_template("add_category.html")
            elif request.method == "POST":
                name = request.form["name"]
                description = request.form["description"]
                stock = request.form["stock"]
                price = request.form["price"]
                img = request.files["img"]
                product = Product(name = name, description = description, stock = stock, owner = user.id, price = price)
                db.session.add(product)
                db.session.commit()
                img.save("./static/products/" + str(product.id) + ".png")
                return redirect("/dashboard")
    return redirect("/")


@app.route("/delete_product/<product_id>", methods = ["GET", "POST"])
def delete_product(product_id):
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.admin:
            if request.method == "GET":
                return render_template("delete_product.html")
            elif request.method == "POST":
                if "yes" in request.form:
                    product = Product.query.filter_by(id = product_id).first()
                    db.session.delete(product)
                    db.session.commit()
                    return redirect("/dashboard")
                else:
                    return redirect("/dashboard")
    return redirect("/")

@app.route("/edit_product/<product_id>", methods = ["GET", "POST"])
def edit_product(product_id):
    if "user" in session:
        user = User.query.filter_by(name=session["user"]).first()
        if user.admin:
            product = Product.query.filter_by(id = product_id).first()
            if request.method == "GET":
                return render_template("edit_product.html", product=product)
            elif request.method == "POST":
                name = request.form["name"]
                description = request.form.get("description", None)
                stock = request.form.get("stock", None)
                price = request.form.get("price", None)
                img = request.files.get("img", None)
                if name:
                    product.name = name
                if description:
                    product.description = description
                if stock:
                    product.stock = stock
                if price:
                    product.price = price
                db.session.commit()
                if img:
                    img.save("./static/products/" + str(product.id) + ".png")
                return redirect("/dashboard")
    return redirect("/")

@app.route("/cart", methods = ["GET", "POST"])
def cart():
    if "user" in session:
        cart = json.loads(session["cart"])
        user = User.query.filter_by(name=session["user"]).first()
        products = [[Product.query.filter_by(id = product_id).first(), cart[product_id]] for product_id in cart.keys()]
        total = sum([int(Product.query.filter_by(id = product_id).first().price) * int(cart[product_id]) for product_id in cart.keys()])
        if request.method == "GET":
            return render_template("cart.html", products = products, total = total)
        else:
            if "remove" in request.form:
                cart.pop(request.form["remove"])
                session["cart"] = json.dumps(cart)
                return redirect("/cart")
            else:
                for product, count in products:
                    product.stock -= int(count)
                    purchase = Purchases(product=product.id, owner=product.owner, customer=user.id, count=count)
                    db.session.add(purchase)
                    db.session.commit()
                session["cart"] = json.dumps(dict())
                return redirect("/")
    return redirect("/")
