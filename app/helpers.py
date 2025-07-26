from flask import Flask, render_template, session, redirect
import sqlite3
import re
from functools import wraps



app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('fruggies.db')
    return conn


def browsecategory(category, description):

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch items from the specified category
    cursor.execute("SELECT * FROM items WHERE category = ?", (category,))
    items = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # If no items found, return an empty list
    if not items:
        items = []

    # If items are found, format them for rendering
    else:
        items = [{'id': item[0], 'name': item[1], 'description': item[2], 'price': item[3]} for item in items]
    
    # Render the template with items
    return render_template("browse.html", category=category.capitalize(), items=items, description=description)


def slugify(s):
    """Convert string to URL-friendly slug."""
    return re.sub(r'[\W_]+', '-', s.strip().lower())


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"