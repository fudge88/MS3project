import os
import json
from flask import Flask, render_template, url_for, flash, redirect, session, request
from forms import RegistrationForm, LoginForm, PostForm
if os.path.exists('env.py'):
    import env
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)


@app.route("/")
def index():
    form = LoginForm()
    if 'username' in session:
        return 'you are logged in as ' + session['username']
    return render_template('login.html', title='Login', form=form)


@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

#User Register 

@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        flash("Chill out, you're already logged in!")
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        account = mongo.db.users
        existing_account = mongo.db.users.find_one({
                                                'username': request.form['username']})
        if existing_account:
            flash(f'Welcome back {form.username.data}!', 'success')
            return redirect(url_for('home'))
        else:
            new_account = {'username': request.form['username']}
            account.insert_one(new_account)
            session['username'] = request.form['username']
            flash(f'Welcome to the family {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

#login

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        flash("Chill out, you're already logged in!")
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        account = mongo.db.users
        existing_account = mongo.db.users.find_one({
                                                'username': request.form['username']})
        if existing_account:
            flash(f'Welcome back {form.username.data}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please register first, to get blending!', 'danger')
            return redirect(url_for('register'))
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    session.pop("username",  None)
    return redirect(url_for("home"))  



@app.route('/')
@app.route('/get_drinks')
def get_drinks():
    return render_template('drinks.html', drinks=mongo.db.drinks.find())


@app.route('/add_drinks')
def add_drinks():
    form = PostForm()
    if form.validate_on_submit():
        flash('Your Smoothie has been added to the collection!')
        return redirect(url_for('home'))
    return render_template('adddrink.html', 
                            categories=mongo.db.drink_categories.find(), form=form, title='New Smoothie')


@app.route('/insert_drink', methods=['POST'])
def insert_drink():
    if request.method == 'POST':
        new_recipe = {
            "drink_name": request.form.get("drink_name").strip(),
            "description": request.form.get("description"),
            "ingredients": request.form.get("ingredients"),
            "directions": request.form.get("directions"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "img_url": request.form.get("img_url"),
            "category_name": request.form.get("category_name")
        }
    drinks = mongo.db.drinks
    drinks.insert_one(request.form.to_dict())
    return redirect(url_for('get_drinks'))


@app.route('/view_card/<card_id>')
def view_card(card_id):
    drink_card = mongo.db.drinks.find_one({"_id": ObjectId(card_id)})
    return render_template("viewcard.html", drink_card=drink_card,
                           title='Smoothie Details')








if __name__ == "__main__":
        app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)