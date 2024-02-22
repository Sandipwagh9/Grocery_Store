import os
from flask import render_template, request, session, redirect ,url_for,flash
from flask import current_app as app
from application.database import db
from application.models import User, Product,Section,Manager,User_Cart
from passlib.hash import pbkdf2_sha256 as passhash


from werkzeug.utils import secure_filename
from flask import send_from_directory



@app.route('/',methods=["GET","POST"])
def Home():
    products = Product.query.all() 
    return render_template('home.html', products=products)

@app.route('/Manager_login',methods=["GET","POST"])
def Manager_login():
    
    if request.method == 'POST':
        Manager_name = request.form['username']
        Password = request.form['password']

        user = Manager.query.filter_by(Manager_name=Manager_name).first()
         
        
        if user and passhash.verify(Password, user.Password):
            session['Manager_name'] = Manager_name
            return redirect('/Manager_dashboard='+Manager_name)
        error_msg = 'Invalid username or password!'
        return render_template('Manager_login.html', message=error_msg)

    return render_template('Manager_login.html')

@app.route('/Manager_register', methods=['GET', 'POST'])
def Manager_register():
    if request.method == 'POST':
        Manager_name = request.form['username']
        Password = request.form['password']
        # print(Manager_name)
        # print(Password)
        if Manager.query.filter_by(Manager_name=Manager_name).first():
            return render_template('Manager_login.html', message='Username already taken!')
        user = Manager(Manager_name, Password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('Manager_login'))
    return render_template('Manager_registration.html')

@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        User_name = request.form['username']
        Password = request.form['password']
        # print(User_name)
        # print(Password)
        if User.query.filter_by(User_name=User_name).first():
            return render_template('User_login.html', message='Username already taken!')
        
        special_char="!@#$%^&*()_"
        if len(Password)<8 or len(Password)>20 or not any(char in special_char for char in Password):
            return render_template('User_registration.html', message='Invalid Password!! Password must contain atleast one special character and the length of password must be in between 8 to 20')
        
        user = User(User_name,Password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('Login'))
    return render_template('User_registration.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/logout", methods = ["GET", "POST"])
def logout():
    if session.get("user_id"):
        session.pop("user_id", None)
        products = Product.query.all() 
        return render_template('home.html', products = products)
    elif session.get("manager_id"):
        session.pop("manager_id", None)
        products = Product.query.all() 
        return render_template('home.html', products = products)
    products = Product.query.all() 
    return render_template('home.html', products = products)

@app.route('/user_dashboard/<string:User_name>', methods=['GET', 'POST'])
def user_dashboard(User_name):
    user_data = User.query.filter_by(User_name=User_name).first()
    categories = Section.query.all()
    cat_product = {cat: cat.products for cat in categories}

    if request.method == "POST":
        search_query = request.form.get('search')
        if search_query:
            search_results = []
            for products in cat_product.values():
                for product in products:
                    if search_query.lower() in product.Product_name.lower():
                        search_results.append(product)
            cat_product = {"Search Results": search_results}

    return render_template('user_dashboard.html', categories=categories, cat_product=cat_product, user_data=user_data)

@app.route('/login',methods=["GET","POST"])
def Login():
    
    if request.method == 'POST':
        User_name = request.form['username']
        Password = request.form['password']

        user = User.query.filter_by(User_name=User_name).first()
         
        if user and passhash.verify(Password, user.Password):
            session['user_id'] = user.User_name
            return redirect(url_for('user_dashboard', User_name=User_name))
        error_msg = 'Invalid username or password!'
        return render_template('User_login.html', message=error_msg)

    return render_template('User_login.html')

@app.route("/Manager_dashboard=<Manager_name>",methods=["POST","GET"])
def Manager_dashboard(Manager_name):
    manager = Manager.query.filter_by(Manager_name = Manager_name ).first()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_category':
            category_name = request.form['categoryName']
            category = Section(Category_name=category_name)
            db.session.add(category)
            db.session.commit()
        
        elif action == 'remove_category':
            category_name = request.form['categoryName']
            category = Section.query.filter_by(Category_name=category_name).first()
            if category:
                products_to_update = Product.query.filter_by(Category_id=category.Category_id).all()
                default_category = Section.query.filter_by(Category_name='Default').first()
                default_category_id = default_category.Category_id if default_category else None

                for product in products_to_update:
                    product.Category_id = default_category_id
                db.session.delete(category)
                db.session.commit()
    
        elif action == 'add_product':
            product_name = request.form['productName']
            rate_per_unit = request.form['rate']
            quantity = request.form['quantity']
            expiry_date = request.form['expiry_date']
            category_id = request.form['Category_id'] 

            
            product_image = request.files.get('productImage')

            if product_image:
                image_filename = secure_filename(product_image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                product_image.save(image_path)

            product = Product(Product_name=product_name, Rate_per_unit=rate_per_unit, Stock=quantity, Expiry_date=expiry_date, Category_id=category_id, Image_url=image_filename,Manager_id = manager.Manager_id)
            db.session.add(product)
            db.session.commit()
    categories = Section.query.all()
    products = Product.query.filter_by(Manager_id = manager.Manager_id).all()
    return render_template("Managers_dashboard.html", categories=categories, products=products, man = manager)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        product.Product_name = request.form['product_name']
        product.Rate_per_unit = request.form['rate']
        product.Quantity = request.form['quantity']
        product.Expiry_date = request.form['expiry_date']
        db.session.commit()

        manager_name = session.get('Manager_name')
        return redirect(url_for('Manager_dashboard', Manager_name=manager_name))

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()
        manager_name = session.get('Manager_name')

        
        return redirect(url_for('Manager_dashboard', Manager_name=manager_name))
    return render_template('delete_product.html', product=product)          


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if "user_id" not in session:
        flash("Log in first","error")
        return redirect(url_for("Login"))
    
    
    if request.method=="POST":
        product_id=int(request.form['product_id'])
        user=User.query.filter_by(User_name=session['user_id']).first()
        if not user:
            flash("User not Found","error")
            return redirect(url_for("Login"))
        
        product = Product.query.get(product_id)
        if not product:
            flash( 'Product not found','error')
            return redirect(url_for("Login"))
        if not user.cart:
            user.cart = User_Cart()
            db.session.commit()
        
        cart=user.cart
        products_in_cart=User_Cart.Cart_products
        print(cart)
        quantity = int(request.form.get('quantity',1))
        
        cart_product = None
        for p in cart.Cart_products:
            if p.Product_id == product.Product_id:
                cart_product = p
                break

        if cart_product:
            cart_product.quantity += quantity
            db.session.commit()
            flash("Updated", "info")
        else:
            cart.Cart_products.append(product)
            product.quantity= quantity
            db.session.commit()
            flash("Added","success")
        return redirect(url_for("user_dashboard",User_name=session['user_id']))
    
    flash("Invalid request","error")
    return redirect(url_for("user_dashboard",User_name=session['user_id']))

@app.route("/cart", methods=["GET"])
def cart():
    if "user_id" not in session:
        flash("Please log in", "error")
        return redirect(url_for("Login"))

    user = User.query.filter_by(User_name=session['user_id']).first()

    if user.cart is None:
        total_price = 0
    else:
        total_price = 0
        for product in user.cart.Cart_products:
            if hasattr(product, "Rate_per_unit") and hasattr(product, "quantity"):
                total_price += product.Rate_per_unit * product.quantity

    return render_template('cart.html', user=user, total_price=total_price)

@app.route("/remove_product_from_user_cart/<int:product_id>",methods=["GET"])
def remove_product_from_user_cart(product_id):
    if "user_id" not in session:
        flash("Plz log in","error")
        return redirect(url_for("Login"))
    user=User.query.filter_by(User_name=session['user_id']).first()
    product = Product.query.get(product_id)
    
    if product in user.cart.Cart_products:
        product_in_cart=[p for p in user.cart.Cart_products if p.Product_id==product.Product_id][0]
        user.cart.Cart_products.remove(product)

        product_in_cart.quantity = 0
        db.session.commit()
        flash("Removed","info")
    return redirect(url_for("cart"))


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if "manager_id" not in session:
        flash("Please log in", "error")
        return redirect(url_for("Manager_login"))

    category = Section.query.get(category_id)

    if request.method == 'POST':
        new_category_name = request.form['new_category_name']
        category.Category_name = new_category_name
        db.session.commit()
        flash("Category updated successfully", "success")
        return redirect(url_for('Manager_dashboard', Manager_name=session['Manager_name']))

    return render_template('edit_category.html', category=category)

@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    if "user_id" not in session:
        flash("Please log in", "error")
        return redirect(url_for("Login"))

    user = User.query.filter_by(User_name=session['user_id']).first()
    product = Product.query.get(product_id)

    if product:
        quantity = int(request.form.get('quantity', 1))

        if quantity > 0 and product.Stock >= quantity:
            product.Stock -= quantity
            user.cart.Cart_products.remove(product)
            db.session.commit()

            flash("Product purchased successfully", "success")
        elif quantity <= 0:
            flash("Invalid quantity. Please enter a positive quantity.", "error")
        else:
            flash("Insufficient stock. Please choose a lower quantity.", "error")

    return redirect(url_for("user_dashboard",User_name=session['user_id']))

@app.route("/reset")
def reset():
    return redirect(url_for("Login"))