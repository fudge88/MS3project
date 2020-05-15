from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
app = Flask(__name__)


app.config['SECRET_KEY'] = '334917b981349a5d0256a084221e6d5dd164'

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)

@app.route("/login")
def login():
    form = RegistrationForm()
    return render_template('login.html', title='Login', form=form)


if __name__  == '__main__':
    app.run(debug=True)