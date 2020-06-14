import os
import json
from flask import Flask, render_template, url_for, flash, redirect, session, request, abort
from forms import RegistrationForm, LoginForm, PostForm
if os.path.exists('env.py'):
    import env
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
import math


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")


mongo = PyMongo(app)
drinks = mongo.db.users.find()


@app.route("/home")
def home():
    form = RegistrationForm()
    return render_template('index.html', form=form, drinks=drinks)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        flash("Chill out, you're already logged in!")
        return redirect(url_for('home'))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            account = mongo.db.users
            existing_account = mongo.db.users.find_one({
                'username': request.form['username']
            })
        else:
            flash(f'Not Allowed', 'danger')
            return redirect(url_for('register'))
        if existing_account:
            flash(f'Welcome back {form.username.data}!', 'success')
            return redirect(url_for('home'))
        else:
            new_account = {'username': request.form['username']}
            account.insert_one(new_account)
            session['username'] = request.form['username']
            flash(f'Welcome to the family {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template(
        'register.html', title='Register', form=form, drinks=drinks
        )


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash('you are logged in as ' + session['username'])
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            account = mongo.db.users
            existing_account = account.find_one({
                'username': request.form['username']
            })
        if existing_account:
            session['username'] = request.form['username']
            flash(f'Welcome back {form.username.data}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please register first, to get blending!', 'danger')
            return redirect(url_for('register'))
    return render_template(
        'login.html', title='Login', form=form, drinks=drinks
        )


@app.route("/logout")
def logout():
    session.pop("username",  None)
    return redirect(url_for("home"))


@app.route('/')
@app.route('/get_drinks')
def get_drinks():
    categories = mongo.db.drink_categories.find()
    limit_per_page = 12
    drink_page = int(request.args.get('drink_page', 1))
    drink_numbers = mongo.db.drinks.count()
    page_number = range(1, int(math.ceil(drink_numbers / limit_per_page)) + 1)
    drinks = mongo.db.drinks.find().sort('_id', pymongo.ASCENDING).skip(
        (drink_page - 1)*limit_per_page).limit(limit_per_page)

    return render_template(
        'drinks.html', drinks=drinks,
        categories=categories, page_number=page_number,
        drink_page=drink_page, drink_numbers=drink_numbers,
        limit_per_page=limit_per_page
        )


@app.route('/drinks/<category>')
def browse_category(category):
    categories = mongo.db.drink_categories.find()
    drinks = mongo.db.drinks.find({'category_name': category})
    return render_template(
        'drinks.html', category=category, drinks=drinks, categories=categories
        )


@app.route('/add_drinks')
def add_drinks():
    if 'username' not in session:
        flash('Please LogIn to add Smoothie', 'danger')
        return redirect(url_for('login'))
    form = PostForm()
    categories = mongo.db.drink_categories.find()
    return render_template(
        'adddrink.html', categories=categories, form=form, drinks=drinks, title='New Smoothie'
        )


@app.route('/insert_drink', methods=['POST'])
def insert_drink():
    form = LoginForm()
    drinks = mongo.db.drinks
    if request.method == 'POST':
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
    if form.validate_on_submit():
        flash('Your Smoothie has been added to the collection!')
        return redirect(url_for('my_drinks'))
    return redirect(url_for('get_drinks'))


@app.route('/view_card/<card_id>')
def view_card(card_id):
    drink_id = mongo.db.drinks.find_one({"_id": ObjectId(card_id)})
    return render_template("viewcard.html", drink_id=drink_id, drinks=drinks,
                           title='Smoothie Details')


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
        print(request.form.get("ingredients"))
        return redirect(url_for('get_drinks'))
    return render_template(
        'editdrinks.html', drink=drink, drinks=drinks,
        categories=mongo.db.drink_categories.find()
        )


@app.route('/delete_drink/<drink_id>', methods=['GET'])
def delete_drink(drink_id):
    drinks = mongo.db.drinks.find_one({'_id': ObjectId(drink_id)})
    if session['username'] == drinks['username']:
        mongo.db.drinks.remove({'_id': ObjectId(drink_id)})
        flash('Your Smoothie has been deleted!', 'success')
        return redirect(url_for('user_posts'))
    else:
        flash('Not allowed, you can only delete your own smoothie!', 'danger')
        return redirect(url_for('home'))


@app.route('/drinks', methods=['GET'])
def user_posts():
    drinks = mongo.db.drinks.find({'username': session['username']})
    return render_template(
            'user_drinks.html', drinks=drinks
            )


if __name__ == "__main__":
        app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)