import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import errorPage, login_required


# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    """Render home page"""

    # Find last quote submitted and populate tweet button with it
    username = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])
    last_quote = db.execute("SELECT * FROM quotes WHERE username = :username ORDER BY quote_id DESC LIMIT 1", username=username[0]["username"])

    # User reached via post
    if request.method == "POST":

        # Ensure a quote was submitted
        if not request.form.get("quote") and not request.form.get("date"):
            return errorPage("You did not write a quote or submit a date", 400)

        # Insert user quote into quote database if user submitted a quote
        username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])
        db.execute("INSERT INTO quotes (username, quote, picture_url, picture_title) VALUES (:user, :quote, :picture_url, :picture_title)",
                    user=username[0]["username"], quote=request.form.get("quote"), picture_url=request.form.get("image_link"), picture_title=request.form.get("image_title"))

    # Show the quotes user has submitted
    username = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])
    quote = db.execute("SELECT * FROM quotes WHERE username=:username", username=username[0]["username"])
    last_quote = db.execute("SELECT * FROM quotes WHERE username = :username ORDER BY quote_id DESC LIMIT 1", username=username[0]["username"])

    return render_template("index.html", quote=quote, last_quote=last_quote, username=username)


@app.route("/login", methods=["GET", "POST"])
def login():

    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return errorPage("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorPage("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return errorPage("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (submitted a form)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return errorPage("must provide username", 400)

        # Ensure username was submitted
        if not request.form.get("firstname"):
            return errorPage("must provide first name", 400)

        # Ensure username was submitted
        if not request.form.get("lastname"):
            return errorPage("must provide  last name", 400)

        # Ensure password was submitted
        elif not request.form.get("email"):
            return errorPage("must provide email", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return errorPage("must confirm password", 400)

        # Ensure password and confirmation are the same
        elif request.form.get("confirmation") != request.form.get("password"):
            return errorPage("password and confirmation do not match", 400)

        # Does password pass strength requirements
        pswd = request.form.get("password")
        if pswd.islower():
            return errorPage("password must contain at least one capital letter")
        elif pswd.isupper():
            return errorPage("password must contain at least one lower case letter")
        elif pswd.isalpha():
            return errorPage("password must contain at least one number")
        elif len(pswd) < 6:
            return errorPage("password must contain at least 6 characters")

        # Encrypt password
        hash = generate_password_hash(request.form.get("password"))

        # Insert user into database
        rows = db.execute("INSERT INTO users (username, firstname, lastname, email, hash) VALUES(:username, :firstname, :lastname, :email, :hash)",
                          username=request.form.get("username"), firstname=request.form.get("firstname"), lastname=request.form.get("lastname"), email=request.form.get("email"), hash=hash)
        if not rows:
            return errorPage("username already exists", 400)

        # Automatically log user in after they register
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    return errorPage(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0", port=port)
