import os
import re
import io
import zlib
from werkzeug.utils import secure_filename
from flask import Response
from cs50 import SQL
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import face_recognition
from PIL import Image
from base64 import b64encode, b64decode
import re
from helpers import apology, login_required
import requests
from bs4 import BeautifulSoup
from flask import abort
import csv

products = []

# Configure application
app = Flask(__name__)
# configure flask-socketio

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.route("/")
@login_required
def home():
    # Pass a variable 'is_home' to the template
    return render_template('layout.html', is_home=True)


@app.route("/home")
@login_required
# def index():
#     # return render_template("index.html")
#     # Get the product data. This could come from a database, an API, etc.
#     products = [
#     {"id": 1, "name": "ELIO Nắng Xuân Unisex", "description": "Đồng hồ ELIO Nắng Xuân 40 mm Unisex EL032-01", "price": "219.000đ", "image": "static/images/product_1.jpg"},
#     {"id": 2, "name": "ELIO Nàng Thơ Unisex", "description": "Đồng hồ ELIO Nàng Thơ 40 mm Unisex EL030-01", "price": "219.000đ", "image": "static/images/product_2.jpg"},
#     {"id": 3, "name": "Đồng hồ Q&Q Nữ", "description": "Đồng hồ Q&Q 34 mm Nữ VQ86J029Y", "price": "290.000đ", "image": "static/images/product_3.jpg"},
#     {"id": 4, "name": "Đồng hồ ELIO Flower Nữ", "description": "Đồng hồ ELIO Flower 32 mm Nữ EL108-01", "price": "290.000đ", "image": "static/images/product_4.jpg"},
#     {"id": 5, "name": "Đồng hồ thông minh BeFit WatchFit", "description": "Đồng hồ thông minh BeFit WatchFit 46.7mm", "price": "640.000đ", "image": "static/images/product_5.jpg"},
#     {"id": 6, "name": "Đồng hồ thông minh BeFit Sporty", "description": "Đồng hồ thông minh BeFit Sporty 2 44.5mm Nâu", "price": "1.190.000đ", "image": "static/images/product_6.jpg"},
    
# ]

#     # Pass the product data to the template
#     return render_template("layout.html", products=products)
def index():
    # Read data from the CSV file
    with open('CSVData/products.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        products = list(reader)

    # Pass the product data to the template
    return render_template("layout.html", products=products)

@app.route("/add_to_cart/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(product_id):
    # Find the product with the given id
    product = next((product for product in products if product["id"] == product_id), None)
    if product is None:
        abort(404)  # If no product with the given id was found, return a 404 error
    # Pass the product to the template
    return render_template("add_to_cart.html", product=product)

@app.route('/shopping_cart')
def shopping_cart():
    # Your code here
    return render_template('shopping_cart.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # Ensure username was submitted
        if not input_username:
            return render_template("login.html", messager=1)

        # Ensure password was submitted
        elif not input_password:
            return render_template("login.html", messager=2)

        # Query database for username
        username = db.execute(
            "SELECT * FROM users WHERE username = :username", username=input_username
        )

        # Ensure username exists and password is correct
        if len(username) != 1 or not check_password_hash(
            username[0]["hash"], input_password
        ):
            return render_template("login.html", messager=3)

        # Remember which user has logged in
        session["user_id"] = username[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", current_page='login')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not input_username:
            return render_template("register.html", messager=1)

        # Ensure password was submitted
        elif not input_password:
            return render_template("register.html", messager=2)

        # Ensure passwsord confirmation was submitted
        elif not input_confirmation:
            return render_template("register.html", messager=4)

        elif not input_password == input_confirmation:
            return render_template("register.html", messager=3)

        # Query database for username
        username = db.execute(
            "SELECT username FROM users WHERE username = :username",
            username=input_username,
        )

        # Ensure username is not already taken
        if len(username) == 1:
            return render_template("register.html", messager=5)

        # Query database to insert new user
        else:
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (:username, :password)",
                username=input_username,
                password=generate_password_hash(
                    input_password, method="pbkdf2:sha256", salt_length=8
                ),
            )

            if new_user:
                # Keep newly registered user logged in
                session["user_id"] = new_user

            # Flash info for the user
            flash(f"Registered as {input_username}")

            # Redirect user to homepage
            return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", current_page='register')


@app.route("/facereg", methods=["GET", "POST"])
def facereg():
    session.clear()
    if request.method == "POST":
        encoded_image = (request.form.get("pic") + "==").encode("utf-8")
        username = request.form.get("name")
        name = db.execute(
            "SELECT * FROM users WHERE username = :username", username=username
        )

        if len(name) != 1:
            return render_template("camera.html", message=1)

        id_ = name[0]["id"]
        compressed_data = zlib.compress(encoded_image, 9)

        uncompressed_data = zlib.decompress(compressed_data)

        decoded_data = b64decode(uncompressed_data)

        new_image_handle = open("./static/face/unknown/" + str(id_) + ".jpg", "wb")

        new_image_handle.write(decoded_data)
        new_image_handle.close()
        try:
            image_of_bill = face_recognition.load_image_file(
                "./static/face/" + str(id_) + ".jpg"
            )
        except:
            return render_template("camera.html", message=5)

        bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

        unknown_image = face_recognition.load_image_file(
            "./static/face/unknown/" + str(id_) + ".jpg"
        )
        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        except:
            return render_template("camera.html", message=2)

        #  commpare faces
        results = face_recognition.compare_faces(
            [bill_face_encoding], unknown_face_encoding
        )

        if results[0]:
            username = db.execute(
                "SELECT * FROM users WHERE username = :username", username="swa"
            )
            session["user_id"] = username[0]["id"]
            return redirect("/home")
        else:
            return render_template("camera.html", message=3)

    else:
        return render_template("camera.html")


@app.route("/facesetup", methods=["GET", "POST"])
def facesetup():
    if request.method == "POST":
        encoded_image = (request.form.get("pic") + "==").encode("utf-8")

        id_ = db.execute(
            "SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"]
        )[0]["id"]
        # id_ = db.execute("SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["id"]
        compressed_data = zlib.compress(encoded_image, 9)

        uncompressed_data = zlib.decompress(compressed_data)
        decoded_data = b64decode(uncompressed_data)

        new_image_handle = open("./static/face/" + str(id_) + ".jpg", "wb")

        new_image_handle.write(decoded_data)
        new_image_handle.close()
        image_of_bill = face_recognition.load_image_file(
            "./static/face/" + str(id_) + ".jpg"
        )
        try:
            bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]
        except:
            return render_template("face.html", message=1)
        return redirect("/home")

    else:
        return render_template("face.html")

# @app.route("/product/<int:product_id>")
# @login_required
# def product_detail(product_id):
#     # Get the product data from the database using the product_id
#     product = db.execute("SELECT * FROM products WHERE id = ?", product_id)

#     # Pass the product data to the template
#     return render_template("product_detail.html", product=product)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", e=e)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
