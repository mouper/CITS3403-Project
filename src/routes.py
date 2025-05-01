from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Set up the SQLite engine.
engine = create_engine("sqlite:///app.db")

@application.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with Session(engine) as session:
            user = session.query(User).filter_by(username=username).first()

            if user and user.verify_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')  # Remove fresh_visit parameter

@application.route('/logout')
@login_required
def logout():
    logout_user()
    # Redirect with fresh=1 to indicate a clean state
    return redirect(url_for('landing', fresh=1))

@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        with Session(engine) as session:
            if session.query(User).filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('signup'))

            user = User(username=username, email=email, display_name=username)
            user.set_password(password)
            session.add(user)
            session.commit()

            flash('Account created! Please login.', 'success')
            return redirect(url_for('login', fresh=1))

    
    return render_template('signup.html')

@application.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")

@application.route('/analytics')
@login_required
def analytics():
    return render_template("analytics.html", title="Analytics")

@application.route('/requests')
@login_required
def requests():
    return render_template("requests.html", title="My Requests")

@application.route('/account')
@login_required
def account():
    return render_template("account.html", title="My Account")