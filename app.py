from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_default_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create DB tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            if User.query.filter_by(username=username).first():
                return "Username already exists."

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration Error: {e}")
            return "Internal Server Error", 500
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))
            return "Invalid credentials"
        except Exception as e:
            print(f"Login Error: {e}")
            return "Internal Server Error", 500
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


