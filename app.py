from flask import Flask, render_template, redirect, request, session
from flask_session import Session

import sqlite3
from helpers import browsecategory, get_db_connection, slugify, usd
import re
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Register slugify filter
app.jinja_env.filters["slugify"] = slugify
app.jinja_env.filters["usd"] = usd

@app.route('/')
def index():
    """Render the home page"""
    return render_template("index.html")


@app.route('/fruggies')
def fruggies():
    """Render the fruggies page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all items in the 'fruggies' category
    cursor.execute("SELECT * FROM items WHERE category = 'fruggies'")
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert items to a list of dictionaries
    items_list = []
    for item in items:
        item_dict = {
            'id': item[0],
            'name': item[1],
            'description': item[2],
            'price': item[3],
            'category': item[4],
        }
        items_list.append(item_dict)

    return render_template("fruggies.html", items=items_list)

      
@app.route('/items/<slug>')
def item(slug):
    """Render the item detail page based on the slugified name"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all items to find the one with the matching slug
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    # Find the item with a matching slugified name
    for item in items:
        item_dict = {
            'id': item[0],
            'name': item[1],
            'description': item[2],
            'price': item[3],
            'category': item[4],
        }
        if slug == re.sub(r'[\W_]+', '-', item_dict['name'].strip().lower()):
            return render_template("item.html", item=item_dict)
        
    # If not found, show 404
    return render_template("item.html", item=None), 404


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User submitted form
    if request.method == "POST":
        # Get username, password, and confirmation from form
        email = request.form.get("email")
        username = request.form.get("username")
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
        
        # Ensure username was submitted
        if not username:
            return render_template("register.html", error="missing username")

        # Ensure password was submitted
        elif not password:
            return render_template("register.html", error="missing password")

        # Ensure passwords match
        elif password != confirmation:
            return render_template("register.html", error="passwords do not match")

        # Try to insert new user into database
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, generate_password_hash(password))
            )
            db.commit()
            cursor.close()
            db.close()

        # If inserting fails, the username must already match one in the database
        except sqlite3.IntegrityError:
            return render_template("register.html", error="username already exists")
        
        # Redirect user to homepage if register was successful
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")