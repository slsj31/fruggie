from flask import Flask, render_template, session, redirect
import sqlite3
import re
from functools import wraps

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('fruggies.db')
    return conn

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