from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, users

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
        
        user = next((u for u in users.values() if u.username == username), None)
        
        if user and user.verify_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Message will show on dashboard
        else:
            flash('Invalid username or password', 'error')
            # No redirect - render template to preserve flash
    
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
        
        # Check if username exists
        if any(u.username == username for u in users.values()):
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create new user (temporary - will disappear on server restart)
        new_id = max(users.keys()) + 1
        users[new_id] = User(new_id, username, password)
        
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


@application.route('/new_tournament')
@login_required
def new_tournament():
    return render_template('new_tournament.html')
