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
        flash(f"Chill out {form.username.data} you're already logged in!")
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


#crud






if __name__ == "__main__":
        app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)