import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from random import randint

from helpers import lookup

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
        return render_template("home.html")

####################################################
# Nieuwe programma's
####################################################
# geeft homepage weer
@app.route("/home", methods=["GET", "POST"])
def home():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get all the checkboxvalues
        string = "codex:"
        preferences = ["nuts","peanuts", "eggs", "soya", "wheat", "fish", "milk", "italien", "mexican", "dutch", "asian", "vegetarien"]
        for preference in preferences:
            if request.form.get(preference) == "true":
                string += '1'
            else:
                string += '0'
        # Get the value amount
        value = request.form.get("value")

        # Put them into the database
        if "user_id" in session:
            print(session["user_id"])
            db.execute("UPDATE users SET value = %s WHERE id = %s", value, session["user_id"])
            db.execute("UPDATE users SET preferences = %s WHERE id = %s", string, session["user_id"])

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
    #return render_template("menu.html")
    # totaal = hoeveelheid recepten
    recepten = []
    totaal = db.execute("SELECT COUNT(*) from recipe")

    # genereert 5 willekeurige verschilende nummers
    while len(recepten) < 5:
        nummer = randint(1, totaal[0]['COUNT(*)'])
        if nummer not in recepten:
            recepten.append(nummer)

    # zet de nummers om in recepten
    week =[]
    for recept in recepten:
        week.append(db.execute("SELECT * FROM recipe WHERE idr=:idr", idr=recept))

    return render_template("menu.html")


@app.route("/recipe", methods =["GET", "POST"])
def recept():
    if request.method == "POST":
        idr= request.form.get("idr")
        recipe = db.execute("SELECT * FROM recipe WHERE idr=:idr", idr=idr)
        #print(recipe)
        # link voor werkend bovenstaande https://stackoverflow.com/questions/17502071/transfer-data-from-one-html-file-to-another

        ingr= recipe[0]['ingredients']
        lijst = [[]]
        i=0
        volgende = False

        # zet ingredient om in leesbare lijst
        for woord in ingr:
            if ";" in woord:
                # woord.replace(';', "a")
                # print(woord)
                # lijst[i].append(woord)
                volgende = True
                lijst[i]= "".join(lijst[i])
                i+=1
            elif volgende == True:
                lijst.append(list())
                lijst[i].append(woord)
                volgende= False
            else:
                lijst[i].append(woord)

        if i < len(lijst):
            lijst[i] = "".join(lijst[i])

        recipe[0]['ingredients'] = lijst
        return render_template("recipe.html", recipe = recipe[0])

    elif request.method=="GET":
        idr = request.args.get("idr")
        recipe = db.execute("SELECT * FROM recipe WHERE idr=:idr", idr=idr)
        if recipe:
            ingr= recipe[0]['ingredients']
            lijst = [[]]
            i=0
            volgende = False

            # zet ingredient om in leesbare lijst
            for woord in ingr:
                if ";" in woord:
                    volgende = True
                    lijst[i]= "".join(lijst[i])
                    i+=1
                elif volgende == True:
                    lijst.append(list())
                    lijst[i].append(woord)
                    volgende= False
                else:
                    lijst[i].append(woord)

            if i < len(lijst):
                lijst[i] = "".join(lijst[i])

            recipe[0]['ingredients'] = lijst
            return render_template("recipe.html", recipe = recipe[0])

        return render_template("home.html")

    else:
        return render_template("home.html")

def preferences():
    preferences = ["nuts","peanuts", "eggs", "soya", "wheat", "fish", "milk", "italien", "mexican", "dutch", "asian", "vegetarien"]
    data = db.execute("SELECT preferences FROM users WHERE id=:id", id=session["user_id"])
    voorkeuren = []
    for i in len(data[0]['preferences']):
        if data[0]['preferences'][i] == "1":
            voorkeuren.append(preferences[i-5])

    allergie = ["nuts","peanuts", "eggs", "soya", "wheat", "fish", "milk"]
    #keuken = ["italien", "mexican", "dutch", "asian"]
    dieet = ["vegetarien"]


    #for string in voorkeuren:
    #    if string in allergie:

    #    elif string in dieet:


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        return ("Stringerror")
    # return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

