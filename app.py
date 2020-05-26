import os
import json
from flask import Flask, render_template, url_for, flash, redirect, session, request
from forms import RegistrationForm, LoginForm
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


@app.route('/get_drinks')
def get_drinks():
    return render_template('display.html', drinks=mongo.db.drinks.find())


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
        flash('You are already logged in!')
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
            new_account = { 'username': request.form['username']}
            account.insert_one(new_account)
            session['username'] = request.form['username']
            flash(f'Welcome to the family {form.username.data}!', 'success')
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "fujeh":
            flash('you have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsucessful. Please register.', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
        app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)