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

# aangepaste functies uit finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

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

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid password", category='danger')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect naar menu als bestaat
        user = get_user()
        menu = database.check(user, "meal")
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

            #Remember which user has logged in
            data = database.user_in_db(username)
            session["user_id"] = data[0]['user_id']

            # Check if the user already made a menu, and if so display that menu
            check = database.check(get_IP(), "meal")
            if len(check) == 1:
                database.ip_to_id(session['user_id'], "meal")
                database.ip_to_id(session['user_id'], "preferences")

                return redirect("/menu")

        # Redirect to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

####################################################
# Nieuwe programma's
####################################################

# Global variables
intolerances = ["tree nut", "gluten", "peanut", "egg", "soy", "grain", "seafood", "dairy"]
diets = ["no diet", "vegetarian", "pescetarian", "vegan"]

# routes
# show homepage
@app.route("/home", methods=["GET", "POST"])
def home():
    # User reached route via POST (as by submitting a form via POST)
    global intolerances

    if request.method == "POST":
        user_id=get_user()

        # Delete the old recipes
        database.del_meal_plan(user_id)

        # Get all the query options
        diet = request.form.get("diet")

        allergy =[]
        for intolerance in intolerances:
            if request.form.get(intolerance) == "true":
                allergy.append(intolerance)
        allergy = ",".join(allergy)

        # Puts intolerances and diet into database
        update_preferences(allergy, diet)

        # Creates a list of 5 meals and puts them into the database
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
        # Renders template with diet and intolerance variable
        return render_template("home.html", diets=diets, intolerances=intolerances)


# Renders the home template with diet and intolerances
@app.route("/", methods=["GET", "POST"])
def find_home():
    global diets
    global intolerances
    return render_template("home.html", diets=diets, intolerances = intolerances)


@app.route("/profile", methods=["GET", "POST"])
def profile():

    # Check if the user is logged in
    if "user_id" not in session:
        return redirect("/login")

    # Get the user id
    user_id = get_user()

    # Get diet, intolerances and favorites from database
    diet = database.get_diet(user_id)
    intolerances = database.get_intolerances(user_id)
    favorites = database.get_favorites(user_id)

    # Renders template with variables
    return render_template("profile.html", diet=diet, intolerances=intolerances, favorites=favorites)


@app.route("/menu", methods=["GET", "POST"])
def menu():

    # Get the user id
    user_id=get_user()

    # Get saved meals from database
    meals = database.get_menu(user_id)

    # Renders template with meals
    return render_template("menu.html", meals=meals)


@app.route("/recipe", methods =["GET", "POST"])
def recipe():

    # User reached route via POST (as by submitting a form via POST)
    if request.method=="GET":

        # Get the recipe id
        idr = request.args.get("id")

        # Lookup the required data with the recipe
        recipe = lookup(idr)

        # Get the recipe image and name
        data = database.get_recipe(idr)

        # Get the data from favorites table in database if the data is not in meals table
        if not data:
            data = database.get_fav_idr(session['user_id'], idr)

        # If meal already in favorites, display unfavorite instead of favorite
        favorite = False
        if "user_id" in session:
            check = database.get_fav_idr(session['user_id'], idr)
            if check:
                favorite = True

        # Renders template with variables
        return render_template("recipe.html", recipe=recipe, data=data, id=idr, favorite=favorite)

    else:
        return redirect("/")


@app.route("/favorite", methods= ['GET', "POST"])
def favorite():

    # Get recipe id and user id
    idr = request.form['idr']
    user_id=session['user_id']

    # Check if entry in favorites
    check = database.get_fav_idr(user_id, idr)

    # If it exist, erase from database
    if check:
        database.del_fav(user_id, idr)

    # If it does not exist, add to
    else:
        database.add_fav(user_id, idr)
    return "200"


@app.route("/reroll", methods =["POST"])
def reroll():

    # Get the user id
    user_id = get_user()

    # Get the recipe id of wanted reroll and delete it
    idr = request.form.get("reroll")
    database.del_meal(idr, user_id)

    # Get a new meal
    intolerances = database.get_intolerances(user_id)
    diet = database.get_diet(user_id)
    query = get_query(diet)
    meal =  get_meal(query, diet, intolerances)

    # Insert meal into database
    database.update_menu(meal, user_id)

    # Redirect to menu
    return redirect("/menu")

@app.route("/new_meal_plan", methods =["POST"])
def new_meal_plan():

    # Get the user id
    user_id = get_user()

    # Delete the old meal plan
    database.del_meal_plan(user_id)


    # Search for diet in database
    diet = database.get_diet(user_id)

    # Search for intolerances in database
    intolerances = database.get_intolerances(user_id)

    # Create 5 meals and puts them into the database
    for food in range(5):
        query = get_query(diet)
        meal =  get_meal(query, diet, intolerances)
        database.update_menu(meal, user_id)

    # Redirect to menu
    return redirect("/menu")

# functies
def get_user():
    # Returns current user
    if "user_id" in session:
        return session['user_id']
    else:
        return get_IP()

def update_preferences(allergy, diet):
    # Current user
    user = get_user()

    # Checks if user set preferences before and update otherwise add
    check = database.check(user, "preferences")
    if check:
        database.update_pref(user, allergy, diet)
    else:
        database.add_pref(user, allergy, diet)
    return