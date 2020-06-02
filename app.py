import os
import json
from flask import Flask, render_template, url_for, flash, redirect, session, request, abort
from forms import RegistrationForm, LoginForm, PostForm
if os.path.exists('env.py'):
    import env
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)




@app.route("/home")
def home():
    return render_template('index.html')


#User Register 

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
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    session.pop("username",  None)
    return redirect(url_for("home"))


@app.route('/')
@app.route('/get_drinks')
def get_drinks():
    return render_template('drinks.html', drinks=mongo.db.drinks.find(), categories=mongo.db.drink_categories.find())

######################################################### How to?????-
################# 1 route for all 3 categories or 1 for each category??????
@app.route('/drinks/<category>')
def browse_category(category):
    categories = mongo.db.drink_categories.find()
    drinks = mongo.db.drinks.find({'category_name': category})
    return render_template('drinks.html', category=category, drinks=drinks, categories=categories)
##########################################################

@app.route('/add_drinks')
def add_drinks():
    if 'username' not in session:
        flash('Please LogIn to add Smoothie', 'danger')
        return redirect(url_for('login'))
    form = PostForm()
    categories = mongo.db.drink_categories.find()
    return render_template('adddrink.html', 
                            categories=categories, form=form, title='New Smoothie')


@app.route('/insert_drink', methods=['POST'])
def insert_drink():
    form = LoginForm()
    drinks = mongo.db.drinks
    if request.method == 'POST':
        drinks.insert_one({"username": session['username'], 
            "drink_name": request.form.get("drink_name"),
            "description": request.form.get("description"),
            "ingredients": request.form.get("ingredients"),
            "directions": request.form.get("directions"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "img_url": request.form.get("img_url"),
            "category_name": request.form.get("category_name")
        })
    if form.validate_on_submit():
        flash('Your Smoothie has been added to the collection!')
        return redirect(url_for('my_drinks'))
    return redirect(url_for('get_drinks'))


@app.route('/view_card/<card_id>')
def view_card(card_id):
    drink_id = mongo.db.drinks.find_one({"_id": ObjectId(card_id)})
    return render_template("viewcard.html", drink_id=drink_id,
                           title='Smoothie Details')


# @app.route('/edit_drink', methods=['POST'])
# def edit_drink():
#     if session.get('username', None) is not None:
#         username = session.get('username')
#         user = mongo.db.users[username]
#         form = LoginForm()
#         drinks = mongo.db.drinks
#     if request.method == 'POST':
#         drinks.update_one({'username': session['username'],
#             "drink_name": request.form.get("drink_name"),
#             "description": request.form.get("description"),
#             "ingredients": request.form.get("ingredients"),
#             "directions": request.form.get("directions"),
#             "serves": request.form.get("serves"),
#             "prep_time": request.form.get("prep_time"),
#             "img_url": request.form.get("img_url"),
#             "category_name": request.form.get("category_name")
#         })
#     if form.validate_on_submit():
#         flash('Your Smoothie has been updated!')
#         return redirect(url_for('my_drinks'), user=user)
#     else:
#         flash('Not allowed, you can only edit your own smoothie!', 'danger')
#         return redirect(url_for('home'))
#     return redirect(url_for('get_drinks'))

###################################need to add sessions- also does not allow edit????
@app.route('/edit_drink/<drink_id>', methods=['GET', 'POST'])
def edit_drink(drink_id):
    #drink = mongo.db.drinks.find_one_or_404({"_id": ObjectId(drink_id)})
    drink = mongo.db.drinks.find_one({"_id": ObjectId(drink_id)}),
    #form = PostForm()
    if request.method == 'POST':
        if session['username'] == drink.username:
            update_smoothie = {
                "drink_name": request.form.get("drink_name"),
                "description": request.form.get("description"),
                "ingredients": request.form.get("ingredients"),
                "directions": request.form.get("directions"),
                "serves": request.form.get("serves"),
                "prep_time": request.form.get("prep_time"),
                "img_url": request.form.get("img_url"),
                "category_name": request.form.get("category_name")
            }
            mongo.db.drinks.update(
                {"_id": ObjectId(drink_id)}, update_smoothie
            )
            return redirect(url_for('get_drinks'))
        else:
            flash('Not allowed, you can only edit your own smoothie!', 'danger')
            return redirect(url_for('home'))

    return render_template('editdrinks.html', drink=drink,
                                categories=mongo.db.drink_categories.find())


#######################does not redirect to home when deleteing someone elses post????
@app.route('/delete_drink/<drink_id>', methods=['GET'])
def delete_drink(drink_id):
    drinks = mongo.db.drinks.find_one({'_id': ObjectId(drink_id)})
    if session['username'] == drinks['username']:
        mongo.db.drinks.remove({'_id': ObjectId(drink_id)})
        flash('Your Smoothie has been deleted!', 'success')
        return redirect(url_for('get_drinks'))
    else:
        flash('Not allowed, you can only delete your own smoothie!', 'danger')
        return redirect(url_for('home'))



####################################### how to pull users posts only???
@app.route('/my_drinks')
def my_drinks(my_drinks):
    user_post = mongo.db.users.find_one({'username': session['username']})['_id']
    user_id = mongo.db.users.find_one({'username': session['username']})['username']
    my_drinks = mongo.db.drinks.find({'username': session[user_post]})
    return render_template("user_drinks.html", my_drinks=my_drinks,
                           username=user_id,
                           title='My Drinks')

if __name__ == "__main__":
        app.run(host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)