import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


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

# Custom filter

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# test database
db = SQL("sqlite:///test.db")


# geeft momenteel error met de huidige login pagina
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                         username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Username not found")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session["user_id"])

        # Redirect user to home page
        flash('Logged in')
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

    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Checks if username/password is given
        if not request.form.get("username"):
            return #apology("must provide username", 400)
        elif not request.form.get("password"):
            return #apology("must provide password", 400)

        # Checks if passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return #apology("passwords do not match", 400)

        # Checks if username is not taken
        username = request.form.get("username")
        rows =  db.execute("SELECT * FROM users WHERE username = %s", username)
        #print(len(rows))
        if len(rows) >= 1:
            return "error"  #apology("username is already taken", 400)

        # Puts username(UN) and password(PW) in database
        else:
            PW = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, PW))

            #Remember which user has logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
                          username=request.form.get("username"))[0]['id']
            print(session["user_id"])

        flash('Registered')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

####################################################
# Nieuwe programma's
####################################################
# geeft homepage weer
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        preferences = {}
        preferences['nuts'] = request.form.get("nuts")
        preferences['eggs'] = request.form.get("eggs")
        preferences['soya'] = request.form.get("soya")
        preferences['wheat'] = request.form.get("wheat")
        preferences['fish'] = request.form.get("fish")
        preferences['milk'] = request.form.get("milk")
        preferences['mexican'] = request.form.get("mexican")
        preferences['dutch'] = request.form.get("dutch")
        preferences['italian'] = request.form.get("italian")
        preferences['vegetarian'] = request.form.get("vegetarian")
        preferences['asian'] = request.form.get("asian")
        print("test")
        if "user_id" in session:
            print(session["user_id"])

        return render_template("menu.html")
    else:
        return render_template("home.html")

@app.route("/", methods=["GET"])
def find_home():
    return render_template("home.html")


#app.route("/")
#def home():
     #return render_template("home.html")
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method != "POST":
        #voorkeuren = db.execute("SELECT * FROM voorkeuren WHERE id=:id", id=session['user_id'])
        # return render_template("profile.html", allergie=voorkeuren[0]['allergie'], kitchen=voorkeuren[0]['kitchen'])
        return render_template("profile.html")
    else:
        # voorkeuren['allergie'] = request.get("allergie)
        # voorkeurn['kitchen']= request.get("kitchen")
        # db.execute("UPDATE voorkeuren SET (allergie, kitchen) VALUES (:allergie, :kitchen)", allergie=voorkeuren['allergie'], kitchen=voorkeuren['kitchen'])
        # return render_template("profile.html", allergie=voorkeuren['allergie'], kitchen=voorkeuren['kitchen'])
        return render_template("profile.html")





@app.route("/menu", methods=["GET", "POST"])

def menu():
    return render_template("menu.html")


@app.route("/recipe")
def recept():
    return render_template("recipe.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        return ("Stringerror")
    # return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function