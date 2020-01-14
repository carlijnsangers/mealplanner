import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Create a dict with all stocks
    stocks = {}
    symbols = db.execute("SELECT symbol FROM potfolio WHERE id = %s", session["user_id"])
    for symbol in symbols:
        symbol = symbol["symbol"]
        stocks[symbol] = lookup(symbol)

    # Find out how much cash the user has
    cash = db.execute("SELECT cash FROM users WHERE id = %s", session["user_id"])[0]["cash"]

    # Calculate the total value the user owns
    total = cash
    price = {}
    added = {}
    for stock in stocks:
        total += db.execute("SELECT shares FROM potfolio WHERE symbol = %s AND id = %s", stock, session["user_id"])[0]["shares"] * stocks[stock]['price']
        price[stock] = usd(stocks[stock]['price'])
        added[stock] = usd(stocks[stock]['price'] * db.execute("SELECT shares FROM potfolio WHERE symbol = %s AND id = %s", stock, session["user_id"])[0]["shares"])


    # Send values to index.html file
    return render_template("index.html", cash=usd(cash), stocks=stocks, db=db, total=usd(total), id_=session["user_id"], price=price, added=added)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get symbol and share value
        shares = request.form.get("shares")
        symbol = request.form.get("symbol")

        # check if valid amount of shares
        if not shares.isdigit() or int(shares) < 0:
            return apology("please enter a valid amount of shares", 400)

        # Check if valid symbol is given
        if symbol.islower():
            return apology("invalid symbol", 400)

        # Check if valid symbol is given
        symbol_dict = lookup(symbol)
        if symbol_dict == None:
            return apology("invalid symbol", 400)

        # Check if shares has input
        elif shares == None:
            return apology("Please enter wanted amount of shares", 400)


        # Check if user has sufficient cash
        else:
            cash = db.execute("SELECT cash FROM users WHERE id = %s", session["user_id"])

            price = symbol_dict["price"]
            cost = float(price) * int(shares)

            # Return error if cash amount insufficient
            if cost > cash[0]["cash"]:
                return apology("insufficient cash", 401)

            # Subtract cash from user
            else:
                new_cash = cash[0]["cash"] - cost
                db.execute("UPDATE users SET cash = %s WHERE id = %s", new_cash, session["user_id"])

                # Check if user already has the stock
                rows = db.execute("SELECT * FROM potfolio WHERE symbol = %s AND id = %s", symbol, session["user_id"])
                if len(rows) >= 1:

                    # Add stocks to existing stocks
                    existing_shares = db.execute("SELECT shares FROM potfolio WHERE symbol = %s", symbol)
                    new_shares = int(shares) + existing_shares[0]['shares']
                    db.execute("UPDATE potfolio SET shares = %s WHERE id = %s AND symbol = %s", new_shares, session["user_id"], symbol)

                # Add stock to portfolio
                else:
                    db.execute("INSERT INTO potfolio (id, shares, symbol) VALUES (%s, %s, %s)",
                                            (session["user_id"]), shares, request.form.get("symbol"))

                # Add transaction to history
                db.execute("INSERT INTO history (symbol, status, price, id) VALUES (%s, %s, %s, %s)", symbol, f"+{shares}", price, session["user_id"])


            flash('Stock bought')
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # get the exchance history
    stocks = db.execute("SELECT * FROM history WHERE id = %s", session["user_id"])
    return render_template("history.html", stocks=stocks)


@app.route("/cashget", methods=["GET", "POST"])
@login_required
def cashget():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        extra = int(request.form.get("cash"))
        cash = db.execute("SELECT cash FROM users WHERE id = %s", session["user_id"])[0]['cash']
        new_cash = cash + extra
        db.execute("UPDATE users SET cash = %s WHERE id = %s", new_cash, session["user_id"])

        flash('cash added')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cashget.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check if symbol is valid
        if lookup(request.form.get("symbol")) == None or request.form.get("symbol") == '':
            return apology("invalid symbol", 400)

        # Create valuables to use in quoted.html
        else:
            name = lookup(request.form.get("symbol"))["name"]
            price = lookup(request.form.get("symbol"))["price"]

            # Display data in quoted.html
            return render_template("quoted.html", price=usd(price), name=name)


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/check", methods=["GET"])
def check():

    # check if that username is in the database
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.args.get("username"))
    if len(rows) == 0:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Checks if username/password is given
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Checks if passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Checks if username is not taken
        username = request.form.get("username")
        rows =  db.execute("SELECT * FROM users WHERE username = %s", username)
        print(len(rows))
        if len(rows) >= 1:
            return apology("username is already taken", 400)

        # Puts username(UN) and password(PW) in database
        else:
            PW = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, PW))

            # Remember which user has logged in
            session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
                          username=request.form.get("username"))[0]['id']

            flash('Registered')
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    symbols = db.execute("SELECT symbol FROM potfolio WHERE id = %s", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check for valid symbol
        wanted_symbol = request.form.get("symbol")
        if wanted_symbol == "Symbol":
            return apology("must select symbol", 400)

        # Check if valid amount of shares are given and if user has that amount
        shares = db.execute("SELECT shares FROM potfolio WHERE id = %s AND symbol = %s", session["user_id"], wanted_symbol)[0]['shares']
        wanted_shares = int(request.form.get("shares"))
        if wanted_shares == '':
            return apology("Please enter wanted amount of shares", 400)
        elif wanted_shares > shares:
            return apology("You do not own that many shares", 400)

        # Check if all shares are sold or a part and delete them
        else:
            new_shares = shares - wanted_shares
            if new_shares == 0:
                db.execute("DELETE FROM potfolio  WHERE id = %s AND symbol = %s", session["user_id"], wanted_symbol)
            else:
                db.execute("UPDATE potfolio SET shares = %s WHERE id = %s AND symbol = %s", new_shares, session["user_id"], wanted_symbol)

            # Add money to cash
            price = lookup(wanted_symbol)['price']
            new_cash = db.execute("SELECT cash FROM users WHERE id = %s", session["user_id"])[0]['cash'] + price * wanted_shares
            db.execute("UPDATE users SET cash = %s WHERE id = %s", new_cash, session["user_id"])

            # Add transaction to history
            db.execute("INSERT INTO history (symbol, status, price, id) VALUES (%s, %s, %s, %s)", wanted_symbol, f"-{wanted_shares}", price,session["user_id"])


        flash('Stock sold')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
