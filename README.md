# Fruggie Number 5
#### Video Demo: https://youtu.be/wSnJC5zv1nw
#### Description:
A flask web app with multiple features of a typical online shop. I created it because my brother has been making cute little frogs out of clay and selling them to his classmates, and I wanted to see what it would be like to make an online shop for them. Below is an explanation of each file in this project.
#### Files:
##### app.py
Contains many Flask features and handles all of the backend of my project.
##### helpers.py
Defines five useful functions for app.py: get_db_connection() to get a connection to the fruggies.db database, slugify() to convert item names into url-friendly slugs (see fruggie.html), login_required to decorate routes to require login, and usd() to format values as usd in webpages that need it.
##### layout.html
The layout that nearly every other webpage follows by using jinja syntax. Contains a basic bootstrap navbar with links to most pages on the site. By using flask-session and a jinja {% if %} conditional to check if there is a user_id present in the current session, this navbar will display "Register" and "Log in" links when the user is signed out and "View Account" and "Logout" links when the user is logged in. The "About" and "View Account" links are disabled since they currently don't link to anything.
##### index.html
The homepage. 
##### fruggies.html
Using Jinja and Python, dynamically displays the names and descriptions of every fruggie in the Fruggies table of fruggies.db in a row of individual Bootstrap cards. Each card has a view details button that links to a route with a slugified version of the fruggie's name. At that route, the user can add the fruggie to their cart (see fruggie.html). Each card could also display images and prices of the fruggies if they were added to the database. 
##### fruggie.html
Displays the details of whichever fruggie in the Fruggies table of fruggies.db has a name that matches the fruggie name slug in the URL. In an HTML and Bootstrap form, the user can select an accessory for their fruggie for an additional cost and the quantity of the fruggie they want. By submitting the form by clicking the button titled "Add to cart", the item details are added to the user's cart by appending a row of item information to session["cart"][].
##### cart.html
If session[cart] is empty, displays "Your cart is empty!" with a Bootstrap button labeled "Start Shopping!" that will redirect the user to fruggies.html. If session[cart] isn't empty, displays everything in session["cart"] in an html table by using a nested for loop to iterate through each item in the cart and the details of each item. The table also displays a grand total that is calculated server side. A button labeled "Place Order", shown underneath the table, redirects the user to `login.html` if the user is not logged in (meaning `session["user_id"]` has no value). If the user is logged in, the order and order details are logged in `fruggies.db`, the cart in the session is cleared, and the user is shown `order-confirmation.html` to show the user that their order has been placed.
##### register.html
Displays a simple Bootstrap form to allow the user to submit an email address, password, and password confirmation to create an account for the site. The information submitted is validated server-side by checking that the email is a valid one and the passwords exist and match. Once this is done, the information is attempted to be inserted into the users table of fruggies.db using a `try:` block. If a `sqlite.IntegrityError` is raised, the email must already have an account tied to it and therefore cannot be used to make another account. Werkzeug.security's generate_password_hash function is used to encrypt the password before it is entered into the database. 

If server-side validation determines that the information submitted is invalid, `return render_template("register.html", error=error)`, where the second `error` represents the error that caused the submission to be invalid. This error is displayed on this page with a `<p>` tag with `Error: {{ error }}` inside.

The backend for this page mostly follows what I wrote for the register page of C$50 Finance. However, I noticed that in the register route of `app.py` of my version of C$50 Finance, I had inconsistencies in my code of whether `request.form.get("")` was written directly into my `if` statements or if a variable was initialized first that represented `request.form.get` and that variable was written into the `if` statement. Consider the following code:
```
username = request.form.get("username")
password = request.form.get("password")

# Ensure username was submitted
if not username:
    return apology("missing username")

# Ensure password was submitted
elif not request.form.get("password"):
    return apology("missing password")

# Ensure passwords match
elif request.form.get("password") != request.form.get("confirmation"):
    return apology("passwords do not match")
```
Note how the first `if` statement uses a variable titled `username` and the second and third `if` statements use `request.form.get`.
I addressed this inconsistency in the following snippet from `app.py` of this project:
```
# Get username, password, and confirmation from form
email = request.form.get("email")
password = request.form.get("password")
confirmation = request.form.get("confirmation")

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
```
This time, I made sure to use variable names in all of my `if` statements. 

Noticing this inconsistency in C$50 Finance and fixing it in my final project gave me an example of what to look out for and avoid when writing code for future projects.

Additionally, I decided that the user must register with an email instead of a password since I'd want this site to email its users about order updates (and potentially subscribe them to a newsletter with new deals by allowing them to click a checkbox during registration that will sign them up for this newsletter).
##### login.html
Similarly to register.html, displays a simple Bootstrap form that allows the user to log in to the site using their email and password. The email and password are validated serverside to ensure they were submitted, that the email matches one in `fruggies.db`, and that the password submitted is correct by using Werkzeug.security's `check_password_hash` function.
##### order-confirmation
Uses `cursor.lastrowid` during checkout to display the autoincrementing id of the user's order. 
##### fruggies.db
Holds user data and product info.

Schema:
```
CREATE TABLE fruggies(
id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
name TEXT UNIQUE NOT NULL,
description TEXT,
size TEXT check(size in ('frug', 'big')) NOT NULL);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL,
password_hash TEXT NOT NULL);

CREATE TABLE accessories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT);

CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, time NUMERIC NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));

CREATE TABLE order_details
(order_id INTEGER,
fruggie_id INTEGER,
accessory_id INTEGER,
unit_price NUMERIC,
quantity INTEGER,
FOREIGN KEY(order_id) REFERENCES orders(id),
FOREIGN KEY(accessory_id) REFERENCES accessories(id),
FOREIGN KEY(fruggie_id) REFERENCES fruggies(id));
```
