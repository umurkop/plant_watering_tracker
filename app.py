import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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
db = SQL("sqlite:///plant.db")

@app.route("/")
@login_required
def index():
    """Show portfolio of plants"""
    user_id = session["user_id"]  

    plants = db.execute("SELECT name, period, last, next FROM plants WHERE user_id = ?", user_id)
    return render_template("index.html", plants=plants)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add plant"""
    if request.method == "POST":
        name = request.form.get("name")
        period = request.form.get("period")                

        if not name:
            return apology("Please enter a plant name!")

        if not period:
            return apology("Please enter a period!")

        try:
            period = int(request.form.get("period"))
        except:
            return apology("Period must be an integer!")

        if period <= 0:
            return apology("Period must be a positive integer!")               

        user_id = session["user_id"]
        db.execute("INSERT INTO plants (user_id, name, period) VALUES (?, ?, ?)", user_id, name, period)
        # print(f'\n\n{name}\n\n')
        # print(f'\n\n{period}\n\n')

        return redirect('/')
    else:
        return render_template("add.html")    

@app.route("/water", methods=["GET", "POST"])
@login_required
def water():
    """Water a plant of yours"""
    user_id = session["user_id"]

    if request.method == "POST":

        plant = request.form.get("plant")        
        last = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d')

        period = db.execute("SELECT period FROM plants WHERE user_id = ? AND name = ?", user_id, plant)[0]["period"]

        next = last + datetime.timedelta(days=period)

        formatted_last = last.strftime('%Y-%m-%d')
        formatted_next = next.strftime('%Y-%m-%d')        
        
        today = datetime.datetime.today()        
        delta = (next - today).days        

        print(f'\n\n{plant}\n\n')
        print(f'\n\n{last}\n\n')
        print(f'\n\n{next}\n\n')
        print(f'\n\n{today}\n\n')
        print(f'\n\n{delta}\n\n')                               

        db.execute("UPDATE plants SET last = ?, next = ? WHERE user_id = ? AND name = ?", formatted_last, formatted_next, user_id, plant)

        # if delta == 0:
            #message = Message("Your plant's watering time is tommorrow!", recipients=[email])
            #mail.send(message)

        return redirect('/')
    else:
        plants = db.execute("SELECT name FROM plants WHERE user_id = ?", user_id)
        return render_template("water.html", plants=plants)

@app.route("/changeperiod", methods=["GET", "POST"])
@login_required
def changeperiod():
    """Change Watering Period"""
    user_id = session["user_id"]

    if request.method == "POST":
        plant = request.form.get("plant")        
        newperiod = request.form.get("newperiod")

        if not newperiod:
            return apology("Please enter a period!")

        try:
            newperiod = int(request.form.get("newperiod"))
        except:
            return apology("Period must be an integer!")

        if newperiod <= 0:
            return apology("Period must be a positive integer!")                                      

        db.execute("UPDATE plants SET period = ? WHERE user_id = ? AND name = ?", newperiod, user_id, plant)

        return redirect('/')
    else:
        plants = db.execute("SELECT name FROM plants WHERE user_id = ?", user_id)
        return render_template("changeperiod.html", plants=plants)     

@app.route("/deleteplant", methods=["GET", "POST"])
@login_required
def deleteplant():
    """Delete a plant of yours"""
    user_id = session["user_id"]

    if request.method == "POST":
        plant = request.form.get("plant")                                              

        db.execute("DELETE FROM plants WHERE user_id = ? AND name = ?", user_id, plant)

        return redirect('/')
    else:
        plants = db.execute("SELECT name FROM plants WHERE user_id = ?", user_id)
        return render_template("deleteplant.html", plants=plants)

@app.route("/addemail", methods=["GET", "POST"])
@login_required
def addemail():
    """Add user's email address"""
    user_id = session["user_id"]

    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            return apology("Please enter an email!")

        db.execute("UPDATE users SET email = ? WHERE id = ?", email, user_id)

        return redirect('/')
    else:
        return render_template("addemail.html")

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Please enter an Username!")
        if not password:
            return apology("Please enter a Password!")
        if not confirmation:
            return apology("Please confirm the Password!")

        if password != confirmation:
            return apology("Passwords do not match!")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/")
        except:
            return apology("Username has already been registered!")
    else:
        return render_template("register.html")

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """Change password"""
    user_id = session["user_id"]
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        search_user = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        if not old_password:
            return apology("Please enter your Old Password!")
        if not new_password:
            return apology("Please enter your New Password!")
        if not confirmation:
            return apology("Please confirm your New Password!")

        if new_password != confirmation:
            return apology("Passwords do not match!")
        if not check_password_hash(search_user[0]["hash"], request.form.get("old_password")):
            return apology("Invalid password!")

        hash = generate_password_hash(new_password)

        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, user_id)
        return redirect("/")
    else:
        return render_template("changepassword.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
