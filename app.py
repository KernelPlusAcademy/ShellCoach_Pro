
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = 'shellcoach_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    commands_run = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            error = 'Username already exists'
        else:
            hashed_pw = generate_password_hash(request.form['password'])
            new_user = User(username=request.form['username'], password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html', error=error)
    
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])


@app.route('/run', methods=['POST'])
def run_command():
    if 'username' not in session:
        return jsonify({'output': 'Unauthorized'}), 403
    command = request.json.get('command')
    user = User.query.filter_by(username=session['username']).first()
    user.commands_run += 1
    db.session.commit()

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
    except Exception as e:
        output = f"Error: {e}"

    return jsonify({'output': output})

@app.route('/explain', methods=['POST'])
def explain_command():
    if 'username' not in session:
        return jsonify({'explanation': 'Unauthorized'}), 403
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    command = request.json.get('command')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "user", "content": f"Explain the Linux command: {command}" }
            ]
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        explanation = f"Error: {e}"

    return jsonify({'explanation': explanation})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
