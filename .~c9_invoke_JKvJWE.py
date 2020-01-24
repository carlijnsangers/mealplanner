import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import random

from helpers import get_meal

from helpers import lookup, get_meal, get_IP


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
            flash("Invalid password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

    # Redirect user to homepage
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Checks if username/password is given
        if not request.form.get("username"):
            flash("Please enter username")
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("Please enter password")
            return render_template("register.html")

        # Checks if passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("passwords do not match")
            return render_template("register.html")

        # Checks if username is not taken
        username = request.form.get("username")
        rows =  db.execute("SELECT * FROM users WHERE username = %s", username)
        if len(rows) >= 1:
            flash("Username is already taken")
            return render_template("register.html")

        # Puts username(UN) and password(PW) in database
        else:
            PW = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, PW))

            #Remember which user has logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
                          username=request.form.get("username"))[0]['id']

            check = db.execute("SELECT user_id FROM meal WHERE user_id=:IP LIMIT 1", IP=get_IP())
            if len(check) == 1:
                db.execute("UPDATE meal SET user_id=:user_id WHERE user_id=:IP", user_id=session['user_id'], IP = get_IP())

        flash('Registered')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

####################################################
# Nieuwe programma's
####################################################

#global variables
intolerances = ["tree nut", "gluten", "peanut", "egg", "soy", "grain", "seafood", "dairy"]
diets = ["no diet", "vegetarian", "pescetarian", "vegan"]
querys = ["pasta", "burger", "salad", "salmon", "chicken", "potatoes", "rice", "pizza", "lasagne", "nasi", "risotto"]


# geeft homepage weer
@app.route("/home", methods=["GET", "POST"])
def home():
    # User reached route via POST (as by submitting a form via POST)
    global intolerances

    if request.method == "POST":

        if "user_id" in session:
            user_id = session["user_id"]
        else:
            user_id = get_IP()

        # Delete the old recipes
        db.execute("DELETE FROM meal WHERE user_id = :user_id", user_id=user_id)

        # Get all the checkboxvalues
        global diets
        global querys

        diet = request.form.get("diet")
        if diet == "vegan" or diet == "vegetarian":
            querys = ["pasta", "salad", "potatoes", "rice", "macaroni"]
        elif diet == 'pescatarian':
            querys = ["pasta", "salad", "salmon", "potatoes", "rice", "macaroni"]

        allergie =[]
        for intolerance in intolerances:
            if request.form.get(intolerance) == "true":
                allergie.append(intolerance)
        allergie = ",".join(allergie)

        meals = {"id":214959,"title":"Macaroni cheese in 4 easy steps","image":"https://spoonacular.com/recipeImages/214959-312x231.jpg","imageType":"jpg"},{"id":1118472,"title":"Baked Macaroni and Cheese","image":"https://spoonacular.com/recipeImages/1118472-312x231.jpg","imageType":"jpg"},{"id":633672,"title":"Baked Macaroni With Bolognese Sauce","image":"https://spoonacular.com/recipeImages/633672-312x231.jpg","imageType":"jpg"},{"id":668066,"title":"Ultimate macaroni cheese","image":"https://spoonacular.com/recipeImages/668066-312x231.jpg","imageType":"jpg"}
        # meals = []
        # for meal in range(5):
        #     meal = str(meal)
        #     while meal == None or len(meal) <= 1 or meal in meals:
        #         query = random.choice(querys)
        #         meal =  get_meal(query, diet, allergie)
        #     meals.append(meal)

        for meal in meals:
                db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
                                            (meal["id"], meal["title"], meal["image"], user_id))

        return redirect("/menu")

    else:
        return render_template("home.html", diets=diets, intolerances=intolerances)

@app.route("/", methods=["GET"])
def find_home():
    global diets
    global intolerances
    return render_template("home.html", diets=diets, intolerances = intolerances)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method != "POST":
        voorkeuren = preferences(session['user_id'])
        print(voorkeuren)
        return render_template("profile.html", voorkeuren=voorkeuren)
    else:
        return render_template("profile.html")



@app.route("/menu", methods=["GET", "POST"])
def menu():
    if "user_id" in session:
        meals = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = session["user_id"])
    else:
        meals = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = get_IP())
    return render_template("menu.html", meals=meals)



@app.route("/recipe", methods =["GET", "POST"])
def recept():
    if request.method=="GET":
        idr = request.args.get("id")

        recipe = lookup(idr)
        data = db.execute("SELECT image, title FROM meal WHERE id = :idr LIMIT 1", idr=idr)
        return render_template("recipe.html", recipe=recipe, data=data, idr=idr)

    else:
        return render_template("home.html")


@app.route("/favorite", methods= ["POST"])
def favorite():
    print("HELLO")
    idr = 1
    data = "a"
    # Hoe haal je de data van een js post op?
    if idr in data:
        idr=idr+1
    return "200"


    idr = request.form.get("idr")
    print(idr)
    check = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND idr=:idr", user_id=session["user_id"], idr=idr)
    if check:
        db.execute("DELETE FROM favorites WHERE user_id=:user_id AND idr=:idr", user_id=session["user_id"], idr=idr)
    else:
        data = db.execute("SELECT image, title FROM meal WHERE id=:idr LIMIT 1", idr=idr)
        db.execute("INSERT INTO favorites (user_id, idr, image, title) VALUES (:user_id, :idr, :image, :title)",
                user_id=session["user_id"], idr=idr, image=data[0]["image"], title=data[0]['title'])
    url = "/recipe?id="+ idr
    return redirect(url)

@app.route("/reroll", methods =["GET", "POST"])
def reroll():
    global diets
    global intolerances
    global querys

    if "user_id" in session:
        user_id = session["user_id"]
    else:
        user_id = get_IP()

    idr = request.form.get("reroll")
    db.execute("DELETE FROM meal WHERE id = :idr AND user_id=:user_id", idr=idr, user_id=user_id)
    query = random.choice(querys)
    meal =  get_meal(query, None, None)
    db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
                                            (meal["id"], meal["title"], meal["image"], user_id))
    return redirect("/menu")

def update_preferences(allergie, dieet):
    if "user_id" in session:
        user= session['user_id']
    else:
        user=get_IP()

    check = db.execute("SELECT * FROM preferences WHERE id=:user_id", user_id=session['user_id'])
    if check:
        db.execute("UPDATE preferences SET allergie=:allergie, dieet=:dieet WHERE id=:user_id", user_id=user, allergie=allergie, dieet=dieet)
    else:
        db.execute("INSERT INTO preferences (id, allergie, dieet) VALUES (:user_id, :allergie, :dieet", user_id=user, allergie=', '.join(allergie), dieet=dieet)
    return

def preferences(user):
    data = db.execute("SELECT allergie, dieet FROM preferences WHERE id=:user", user=user)
    if data:
        return data
    return {
        "allergie": None,
        "dieet": None
    }

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        return ("Stringerror")
    # return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
