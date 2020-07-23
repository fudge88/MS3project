import os
import json
from flask import Flask, render_template, url_for, flash, \
    redirect, session, request
from forms import RegistrationForm, LoginForm, PostForm
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
import math
if os.path.exists('env.py'):
    import env


# Installation of Flask-PyMongo
app = Flask(__name__)
# links to env.py file
app.secret_key = os.environ.get('SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)


# Global Variable
drinks = mongo.db.users.find()


"""
Login Functions
"""


# Register Function
"""
This route first checks if the user is already logged in.
It calls upon the RegistrationForm() from forms.py, this checks
if the username exists in the DB using the find_one() method.
If an existing username if found, the user will be logged in.
If all scenarios are exhausted, this route will CREATE a new user.
"""


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        flash(f"You are already logged in as {session['username']}!")
        return redirect(url_for('user_posts'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            account = mongo.db.users
            existing_account = mongo.db.users.find_one({
                'username': request.form['username']
            })
        else:
            flash(
                'Please check the username typed meets the requirements'
                )
            return redirect(url_for('register'))
        if existing_account:
            session['username'] = request.form['username']
            flash(f'Welcome back {form.username.data}!')
            return redirect(url_for('get_drinks'))
        else:
            new_account = {'username': request.form['username']}
            account.insert_one(new_account)
            session['username'] = request.form['username']
            flash(f'Welcome to Tutti Smooti & Co. {form.username.data}!')
            return redirect(url_for('home'))
    return render_template(
        'register.html', title='Register', form=form, drinks=drinks
        )


# Login Function
"""
This route first checks if user is logged in.
It calls upon the LoginForm() from forms.py, this checks
if the username exists in the DB using the find_one() method.
If an existing username if found, the user will be logged in.
If all scenarios are exhausted, this route will redirect the
user to teh register page.
"""


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash(f"you are logged in as {session['username']}")
        return redirect(url_for('user_posts'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            account = mongo.db.users
            existing_account = account.find_one({
                'username': request.form['username']
                })
            if existing_account:
                session['username'] = request.form['username']
                flash(f'Welcome back {form.username.data}!')
                return redirect(url_for('user_posts'))
        else:
            flash('Please register first, to get blending!')
            return redirect(url_for('register'))
    return render_template(
        'login.html', title='Login', form=form, drinks=drinks
        )


# logout function
"""
This route runs a function which ends the 'user session',
when invoked this logs the user out, and redirects them to home.
This route also flashes a message to confirm the user has been logged out.
"""


@app.route("/logout")
def logout():
    session.pop("username",  None)
    flash('You have been logged out')
    return redirect(url_for("home"))


"""
Page Functions
"""


# Home
"""
This route runs the functions on the home page.
This route calls for the RegistrationForm() from forms.py, this
works in conjunction with the registration propmt on the home page,
when submitted the function is passed to the registration route from
the html page. If a specific categroy button has been selected on
the html page, the categories variable will allow this function to run.
"""


@app.route('/')
@app.route("/home")
def home():
    form = RegistrationForm()
    categories = mongo.db.drink_categories.find()
    return render_template(
        'index.html', form=form, drinks=drinks, categories=categories
        )


# Show All Smoothies
"""
This route calls all drinks from the DB to be displayed on the
html page. Pagination has been incorporated, allowing no more then
12 drinks to be displayed per page. The math.ceil() method takes a
parameter of a integar, in this case the number of drinks in the DB,
which is divided by 12. +1 adds a new page number as required.
The results are sorted using _id in a decending order.
"""


@app.route('/get_drinks')
def get_drinks():
    categories = mongo.db.drink_categories.find()
    limit_per_page = 12
    drink_page = int(request.args.get('drink_page', 1))
    drink_numbers = mongo.db.drinks.count()
    page_number = range(1, int(math.ceil(drink_numbers / limit_per_page)) + 1)
    drinks = mongo.db.drinks.find().sort('_id', pymongo.DESCENDING).skip(
        (drink_page - 1)*limit_per_page).limit(limit_per_page)
    return render_template(
        'drinks.html', drinks=drinks,
        categories=categories, page_number=page_number,
        drink_page=drink_page, drink_numbers=drink_numbers,
        limit_per_page=limit_per_page
        )


# Filter Catergories
"""
This route searches the catergory collection in the DB, this has a
1 to many relationship, and is able to pull drinks that share the same key.
Pagination has been incorporated into this, so catergory results also
adopt the systematic display of 12 drinks per page.
"""


@app.route('/drinks/<category>')
def browse_category(category):
    categories = mongo.db.drink_categories.find()
    drinks = mongo.db.drinks.find({'category_name': category})
    drink_numbers = drinks.count()
    limit_per_page = 12
    drink_page = int(request.args.get('drink_page', 1))
    page_number = range(1, int(math.ceil(drink_numbers / limit_per_page)) + 1)
    drinks = drinks.sort('_id', pymongo.DESCENDING).skip(
        (drink_page - 1)*limit_per_page).limit(limit_per_page)
    return render_template(
        'drinks.html', category=category, drinks=drinks, categories=categories,
        drink_numbers=drink_numbers, limit_per_page=limit_per_page,
        page_number=page_number
        )


# Add Smoothie
"""
This route checks if teh user is logged in before it redirects to
the add drink page. This then calls upon the PostForm() from the forms.py
file which allows the user to key in recipe as secified. However this does
not insert the recipe into the DB, this just allows the data to be added
into the form this route works in conjunction with insert_drinks route.
The categories variable allows jinja to loop the categories in a drop
down option inthe html.
"""


@app.route('/add_drinks')
def add_drinks():
    if 'username' not in session:
        flash('Please Login to add Smoothie')
        return redirect(url_for('login'))
    form = PostForm()
    categories = mongo.db.drink_categories.find()
    return render_template(
        'adddrink.html', categories=categories, form=form,
        drinks=drinks, title='New Smoothie'
        )


# Insert Smoothie
"""
This route works in conjunction with the add_drinks route, once
the data has been keyed in as specified this route pushes the info
to the DB. The parenthesis uses the 'name' key in the html page to
collect the new data.
The username that is currently in session is recorded as a value for
the username key, thus recording the author of the smoothie.
The method .insert_one() is used to push the data to the DB, if
successful the user will recieve a flash message.
"""


@app.route('/insert_drink', methods=['POST'])
def insert_drink():
    drinks = mongo.db.drinks
    drinks.insert_one(
        {"username": session['username'],
            "drink_name": request.form.get("drink_name"),
            "description": request.form.get("description"),
            "ingredients": request.form.get("ingredients").splitlines(),
            "directions": request.form.get("directions"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "img_url": request.form.get("img_url"),
            "category_name": request.form.get("category_name")}
    )
    flash('Your Smoothie has been added to the collection!')
    return redirect(url_for('user_posts'))


# View Single Smoothie
"""
This route allows the user to get single recipes using the 'drink_id
variable. The variables path seeks the id associated to the specific
ObjectId to the drink the user has requested to see.
"""


@app.route('/view_card/<card_id>')
def view_card(card_id):
    drink_id = mongo.db.drinks.find_one({"_id": ObjectId(card_id)})
    return render_template("viewcard.html", drink_id=drink_id, drinks=drinks,
                           title='Smoothie Details')


# Edit Smoothie
"""
This route works simularly to the 'insert_drink' route, with a
change of method. Here the update() method is used instead of
insert_one() method.
"""


@app.route('/edit_drink/<drink_id>', methods=['GET', 'POST'])
def edit_drink(drink_id):
    drink = mongo.db.drinks.find_one({"_id": ObjectId(drink_id)})
    if request.method == 'POST':
        update_smoothie = {
            "username": session['username'],
            "drink_name": request.form.get("drink_name"),
            "description": request.form.get("description"),
            "ingredients": request.form.get("ingredients").splitlines(),
            "directions": request.form.get("directions"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "img_url": request.form.get("img_url"),
            "category_name": request.form.get("category_name")
        }
        mongo.db.drinks.update(
                {"_id": ObjectId(drink_id)}, update_smoothie
            )
        return redirect(url_for('user_posts'))
    return render_template(
        'editdrinks.html', drink=drink, drinks=drinks,
        categories=mongo.db.drink_categories.find()
        )


# Delete Smoothie
"""
This route uses the _id and objectId to select a specific drink.
The route then checks if the user logged in is the same as the author
of the drink, if a match is made the remove() method then deletes the
drink, and teh user recieved a confirmation flash message. If a match
is not made the user is redirected, and are informed they dont have
authority.
"""


@app.route('/delete_drink/<drink_id>', methods=['GET'])
def delete_drink(drink_id):
    drinks = mongo.db.drinks.find_one({'_id': ObjectId(drink_id)})
    if session['username'] == drinks['username']:
        mongo.db.drinks.remove({'_id': ObjectId(drink_id)})
        flash('Your Smoothie has been deleted!')
        return redirect(url_for('user_posts'))
    else:
        flash('Not allowed, you can only delete your own smoothie!')
        return redirect(url_for('get_drinks'))


# Users Smoothies
"""
This route allows the user that is currently logged in to see
the drinks that they have added to the website. This is done by matching
the DB username key with the session username.
"""


@app.route('/drinks', methods=['GET'])
def user_posts():
    drinks = mongo.db.drinks.find({'username': session['username']})
    return render_template(
            'user_drinks.html', drinks=drinks
            )


if __name__ == "__main__":
    app.run(host=os.environ.get("IP", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
