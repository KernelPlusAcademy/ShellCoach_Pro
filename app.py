from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import subprocess

# Load environment variables
load_dotenv()

# App configuration
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "defaultsecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# OpenAI API setup (optional, for AI explanation mode)
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create tables if needed
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
            
            new_user =_
