import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import random
from helpers import lookup, get_meal, get_IP, get_query
import database

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

# test database
db = SQL("sqlite:///test.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter username", category='danger')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter password", category='danger')
            return render_template("login.html")

        # Query database for username
        rows = database.user_in_db(request.form.get('username'))
        # rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                  username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid password", category='danger')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect naar menu als bestaat
        user = get_user()
        menu = database.check(user, "meal")
        # menu = db.execute("SELECT * FROM meal WHERE user_id=:user LIMIT 1", user=user)
        if menu:
            return redirect("/menu")
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
            flash("Please enter username", category='danger')
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("Please enter password", category='danger')
            return render_template("register.html")

        # Checks if passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("passwords do not match", category='danger')
            return render_template("register.html")

        # Checks if username is not taken
        username = request.form.get("username")
        rows = database.user_in_db(username)
        #rows =  db.execute("SELECT * FROM users WHERE username = %s", username)
        if len(rows) >= 1:
            flash("Username is already taken", category='danger')
            return render_template("register.html")

        # Puts username(UN) and password(PW) in database
        else:
            PW = generate_password_hash(request.form.get("password"))
            database.insert_in_users(username, PW)
            # db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, PW))

            #Remember which user has logged in
            data = database.user_in_db(username)
            session["user_id"] = data[0]['id']
            # session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
            #               username=request.form.get("username"))[0]['id']

            check = database.check(session['user_id'], "meal")
            #check = db.execute("SELECT user_id FROM meal WHERE user_id=:IP LIMIT 1", IP=get_IP())
            if len(check) == 1:
                database.ip_to_id(session['user_id'])
                # db.execute("UPDATE meal SET user_id=:user_id WHERE user_id=:IP", user_id=session['user_id'], IP = get_IP())

        #flash('Registered')
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

# routes
# geeft homepage weer
@app.route("/home", methods=["GET", "POST"])
def home():
    # User reached route via POST (as by submitting a form via POST)
    global intolerances

    if request.method == "POST":
        user_id=get_user()

        # Delete the old recipes
        db.execute("DELETE FROM meal WHERE user_id = :user_id", user_id=user_id)

        # Get all the query options
        diet = request.form.get("diet")

        allergy =[]
        for intolerance in intolerances:
            if request.form.get(intolerance) == "true":
                allergy.append(intolerance)
        allergy = ",".join(allergy)

        update_preferences(allergy, diet)
        # meals = {"id":214959,"title":"Macaroni cheese in 4 easy steps","image":"https://spoonacular.com/recipeImages/214959-312x231.jpg","imageType":"jpg"},{"id":1118472,"title":"Baked Macaroni and Cheese","image":"https://spoonacular.com/recipeImages/1118472-312x231.jpg","imageType":"jpg"},{"id":633672,"title":"Baked Macaroni With Bolognese Sauce","image":"https://spoonacular.com/recipeImages/633672-312x231.jpg","imageType":"jpg"},{"id":668066,"title":"Ultimate macaroni cheese","image":"https://spoonacular.com/recipeImages/668066-312x231.jpg","imageType":"jpg"}
        meals = []
        for meal in range(5):
            meal = str(meal)
            while meal == None or len(meal) <= 1 or meal in meals:
                query = get_query(diet)
                meal =  get_meal(query, diet, allergy)
            meals.append(meal)
            database.update_menu(meal, user_id)

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
    if "user_id" not in session:
        return redirect("/login")
    user_id = get_user()
    diet = database.get_diet(user_id)
    intolerances = database.get_intolerances(user_id)
    favorites = db.execute("SELECT * FROM favorites WHERE user_id=:user_id", user_id=user_id)
    return render_template("profile.html", diet=diet, intolerances=intolerances, favorites=favorites)


@app.route("/menu", methods=["GET", "POST"])
def menu():
    user_id=get_user()
    meals = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = user_id)
    return render_template("menu.html", meals=meals)

@app.route("/recipe", methods =["GET", "POST"])
def recipe():
    if request.method=="GET":
        idr = request.args.get("id")
        recipe = lookup(idr)
        data = db.execute("SELECT image, title FROM meal WHERE id = :idr LIMIT 1", idr=idr)
        favorite = False
        if "user_id" in session:
            check = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND idr=:idr", user_id=session['user_id'], idr=idr)
            if check:
                favorite = True
        return render_template("recipe.html", recipe=recipe, data=data, idr=idr, favorite=favorite)

    else:
        return redirect("/")

@app.route("/favorite", methods= ['GET', "POST"])
def favorite():

    # print(request.form['idr'])
    idr = request.form['idr']
    user_id=session['user_id']

    check = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND idr=:idr", user_id=user_id, idr=idr)
    if check:
        db.execute("DELETE FROM favorites WHERE user_id=:user_id AND idr=:idr", user_id=user_id, idr=idr)
    else:
        data = db.execute("SELECT image, title FROM meal WHERE id=:idr LIMIT 1", idr=idr)
        db.execute("INSERT INTO favorites (user_id, idr, image, title) VALUES (:user_id, :idr, :image, :title)",
                user_id=user_id, idr=idr, image=data[0]["image"], title=data[0]['title'])
    return


@app.route("/reroll", methods =["POST"])
def reroll():
    # global querys
    user_id = get_user()
    idr = request.form.get("reroll")
    database.del_meal(idr, user_id)
    diet = database.get_diet(user_id)
    query = get_query(diet)
    meal =  get_meal(query, diet, None)
    db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
                                            (meal["id"], meal["title"], meal["image"], user_id))
    return redirect("/menu")


@app.route("/new_meal_plan", methods =["POST"])
def new_meal_plan():
    user_id = get_user()

    diet = database.get_diet(user_id)
    print(diet)
    intolerances = database.get_intolerances(user_id)
    print(intolerances)
    database.del_meal_plan(user_id)
    for food in range(5):
        query = get_query(diet)
        print(query)
        meal =  get_meal(query, diet, intolerances)
        print(meal)
        database.update_menu(meal, user_id)

    return redirect("/menu")


# functies
def get_user():
    # returnt huidige gebruiker
    if "user_id" in session:
        return session['user_id']
    else:
        return get_IP()

def update_preferences(allergy, diet):
    # huidige gebruiker
    user = get_user()

    # kijkt of gebruiker al eerder voorkeuren heeft opgegeven en update anders voegt toe
    check = db.execute("SELECT * FROM preferences WHERE id=:user_id", user_id=user)
    if check:
        db.execute("UPDATE preferences SET allergy=:allergy, diet=:diet WHERE id=:user_id", user_id=user, allergy=allergy, diet=diet)
    else:
        db.execute("INSERT INTO preferences (id, allergy, diet) VALUES (:user_id, :allergy, :diet)",
                user_id=user, allergy=allergy, diet=diet)
    return


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        return ("Stringerror")
    # return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)