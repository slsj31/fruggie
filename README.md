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
##### register.html
Displays a simple Bootstrap form to allow the user to submit an email address, password, and password confirmation to create an account for the site. After the information submitted is validated server-side by checking that the email is a valid one and the passwords exist and match, the information is inserted into the users table of fruggies.db. Werkzeug.security's generate_password_hash function is used to encrypt the password before it is entered.
