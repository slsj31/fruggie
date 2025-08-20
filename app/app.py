from flask import Flask, render_template, redirect, request, session
from flask_session import Session

import sqlite3
from helpers import get_db_connection, slugify, usd, login_required
import re
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Register filters
app.jinja_env.filters["slugify"] = slugify
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Prices
FRUGGIE_PRICE = 3
ACCESSORY_PRICE = 0.5


@app.route('/')
def index():
    """Render the home page"""
    return render_template("index.html")


@app.route('/fruggies')
def fruggies():
    """Render the fruggies page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all fruggies from the database
    cursor.execute("SELECT * FROM fruggies")
    fruggies = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to a list of dictionaries
    fruggies_list = []
    for fruggie in fruggies:
        fruggie_dict = {
            'id': fruggie[0],
            'name': fruggie[1],
            'description': fruggie[2],
            'size': fruggie[3],
            'price': 3,
        }
        fruggies_list.append(fruggie_dict)

    return render_template("fruggies.html", fruggies=fruggies_list)

      
@app.route('/fruggies/<slug>')
def fruggie(slug):
    """Render the item detail page based on the slugified name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all fruggies to find the one with the matching slug
    cursor.execute("SELECT * FROM fruggies")
    fruggies = cursor.fetchall()

    # Fetch all accessories
    cursor.execute("SELECT * FROM accessories")
    accessories = cursor.fetchall()

    # Close the database connection
    cursor.close() 
    conn.close()

    # Convert accessories to a list of dictionaries
    accessories_list = []
    for accessory in accessories:
        accessory_dict = {
            'id': accessory[0],
            'name': accessory[1],
        }
        accessories_list.append(accessory_dict)

    # Find the item with a matching slugified name
    for fruggie in fruggies:
        fruggie_dict = {
            'id': fruggie[0],
            'name': fruggie[1],
            'description': fruggie[2],
            'price': FRUGGIE_PRICE,
        }

        if slug == re.sub(r'[\W_]+', '-', fruggie_dict['name'].strip().lower()):
            return render_template("fruggie.html", fruggie=fruggie_dict, accessories=accessories_list)

    # If not found, redirect to the fruggies page
    return redirect("/fruggies")


@app.route("/about")
def about():
    """Render the about page"""
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User submitted form
    if request.method == "POST":
        # Get username, password, and confirmation from form
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Connect to the database
        db = get_db_connection()
        cursor = db.cursor()

        # Ensure email was submitted
        if not email:
            return render_template("register.html", error="missing email")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template("register.html", error="invalid email")

        # Ensure password was submitted
        elif not password:
            return render_template("register.html", error="missing password")

        # Ensure passwords match
        elif password != confirmation:
            return render_template("register.html", error="passwords do not match")

        # Try to insert new user into database
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(password))
            )
            db.commit()
            cursor.close()
            db.close()

        # If inserting fails, the username must already match one in the database
        except sqlite3.IntegrityError:
            return render_template("register.html", error="there is already an account with that email")
        
        # Redirect user to login if register was successful
        return redirect("/login")

    # User reached route via GET
    else:
        return render_template("register.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User submitted form
    if request.method == "POST":
        # Get username and password from form
        email = request.form.get("email")
        password = request.form.get("password")

        print(email, password)

        # Connect to the database
        db = get_db_connection()
        cursor = db.cursor()

        # Ensure username was submitted
        if not email:
            return render_template("login.html", error="missing email")

        # Ensure password was submitted
        elif not password:
            return render_template("login.html", error="missing password")

        # Query database for user with matching username
        cursor.execute("SELECT * FROM users WHERE email = ?", [email])
        user = cursor.fetchone()
        
        # If user does not exist or password is incorrect, show error
        if user is None or not check_password_hash(user[2], password):
            return render_template("login.html", error="invalid email and/or password")

        # Store user ID in session
        session["user_id"] = user[0]
        
        # Redirect user to homepage if login was successful
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""
    # Clear the session
    session.clear()
    
    # Redirect user to homepage
    return redirect("/")


@app.route("/cart")
def cart():
    """Render the cart page"""

    # Get the cart items from the session
    cart_items = session.get("cart", [])
    if not cart_items:
        return render_template("cart.html", cart_items=[])
    
    # Connect to the database to fetch item details
    conn = get_db_connection()
    cursor = conn.cursor()

    # Initialize total price
    total_price = 0

    # Fetch details for each item in the cart
    for item in cart_items:
        fruggie_id = item["fruggie_id"]
        accessory_id = int(item["accessory_id"])
        quantity = int(item["quantity"])

        # Fetch fruggie details
        cursor.execute("SELECT name, description FROM fruggies WHERE id = ?", (fruggie_id,))
        fruggie = cursor.fetchone()
        item["fruggie"] = {
            "name": fruggie[0],
            "description": fruggie[1],
            "price": FRUGGIE_PRICE,
        }

        # Set the price for the fruggie
        item["unit_price"] = FRUGGIE_PRICE

        # Fetch accessory details if available
        if accessory_id != 0:
            cursor.execute("SELECT name FROM accessories WHERE id = ?", (accessory_id,))
            accessory = cursor.fetchone()
            item["accessory"] = {
                "name": accessory[0],
                "price": ACCESSORY_PRICE,
            }
            item["unit_price"] += ACCESSORY_PRICE  # Add accessory price to total
        
        # Calculate total price for this item
        item["total_price"] = item["unit_price"] * quantity
        total_price += item["total_price"]

    # Convert cart items to a list of dictionaries
    cart_items = [{
        'fruggie': item['fruggie'], 
        'accessory': item.get('accessory'), 
        'quantity': item['quantity'], 
        'unit_price': item['unit_price'],
        'total_price': item['total_price'],
    } for item in cart_items]

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Add item to cart"""
    
    # Get the item ID and quantity from the form
    fruggie_id = request.form.get("fruggie_id")
    accessory_id = request.form.get("accessory_id")
    quantity = request.form.get("quantity")

    # Insert the item into the cart
    session["cart"] = session.get("cart", [])
    session["cart"].append({
        "fruggie_id": fruggie_id,
        "accessory_id": accessory_id,
        "quantity": quantity
    })

    # Redirect to the cart
    return redirect("/cart")


@app.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    """Checkout the cart"""
    
    # Get the cart items from the session
    cart_items = session.get("cart", [])
    if not cart_items:
        return redirect("/cart")

    # Store the order in database
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session["user_id"]
    cursor.execute("INSERT INTO orders (user_id, time) VALUES (?, datetime('now'))", (user_id,))
    order_id = cursor.lastrowid

    # Store the order details in database
    for item in cart_items:
        fruggie_id = item["fruggie_id"]
        accessory_id = item.get("accessory_id")
        unit_price = item["unit_price"]
        quantity = int(item["quantity"])

        cursor.execute(
            "INSERT INTO order_details VALUES (?, ?, ?, ?, ?)",
            (order_id, fruggie_id, accessory_id, unit_price, quantity)
        )
        
    # Clear the cart from the session
    session["cart"] = []

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    # Redirect to a confirmation page
    return render_template("order-confirmation.html", order_id=order_id)





