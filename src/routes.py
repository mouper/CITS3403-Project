from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, UserStat, Tournament, TournamentPlayer
from db import db  # Use the centralized db object from db.py
import json

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

        user = db.session.query(User).filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing', fresh=1))

@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        errors = []

        if db.session.query(User).filter_by(username=username).first():
            errors.append("Username already exists.")

        if db.session.query(User).filter_by(email=email).first():
            errors.append("Email already in use.")

        if not password or password.strip() == "":
            errors.append("Password cannot be empty.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('signup'))

        user = User(username=username, email=email, display_name=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

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
    user_stats = db.session.query(UserStat).filter_by(user_id=current_user.id).all()
    return render_template("analytics.html", title="Analytics", stats=user_stats)

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

@application.route('/save_tournament', methods=['POST'])
@login_required
def save_tournament():
    try:
        # Get JSON data from request
        data = request.json
        
        # Validate player usernames before making any database changes
        invalid_usernames = []
        for i, player_data in enumerate(data.get('players', [])):
            # Check if this player entry specifies a TourneyPro username
            if 'username' in player_data and player_data['username'] and not (
                # Skip validation for player 1 when it's the current user
                i == 0 and data.get('include_creator_as_player', False) and 
                player_data.get('user_id') == current_user.id
            ):
                # Verify username exists in the database
                existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
                if not existing_user:
                    invalid_usernames.append(player_data['username'])
        
        # If any invalid usernames were found, return an error
        if invalid_usernames:
            return jsonify({
                'success': False,
                'message': f"Invalid TourneyPro username(s): {', '.join(invalid_usernames)}",
                'invalid_usernames': invalid_usernames
            }), 400
            
        # Create new tournament
        new_tournament = Tournament(
            title=data['title'],
            format=data['format'],
            game_type=data['game_type'],
            created_by=current_user.id,
            is_draft=data['is_draft'],
            include_creator_as_player=data['include_creator_as_player']
        )
        
        # Add tournament to database and flush to get ID
        db.session.add(new_tournament)
        db.session.flush()
        
        # Process players
        for player_data in data['players']:
            new_player = TournamentPlayer(
                tournament_id=new_tournament.id,
                guest_name=player_data.get('guest_name', ''),
                email=player_data.get('email', ''),
                is_confirmed=player_data.get('is_confirmed', False)
            )
            
            # If user_id is provided, use it
            if 'user_id' in player_data and player_data['user_id']:
                new_player.user_id = player_data['user_id']
            # If username is provided, try to match by username
            elif 'username' in player_data and player_data['username']:
                existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
                if existing_user:
                    new_player.user_id = existing_user.id
            # Try to match user by email if provided
            elif player_data.get('email'):
                existing_user = db.session.query(User).filter_by(email=player_data['email']).first()
                if existing_user:
                    new_player.user_id = existing_user.id
            
            db.session.add(new_player)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tournament_id': new_tournament.id,
            'message': 'Tournament saved successfully'
        })
        
    except Exception as e:
        # Roll back any changes if error occurs
        db.session.rollback()
        print(f"Error saving tournament: {str(e)}")
        
        return jsonify({
            'success': False,
            'message': f"Error saving tournament: {str(e)}"
        }), 500

@application.route('/upload_tournament_data', methods=['POST'])
@login_required
def upload_tournament_data():
    uploaded_file = request.files.get('file')

    if not uploaded_file or not uploaded_file.filename.endswith('.json'):
        flash("Please upload a valid .json file.", "error")
        return redirect(url_for('dashboard'))

    try:
        data = json.load(uploaded_file)
        print("Parsed tournament data:", data)  # 🐛 Debug print for now

        # Use the JSON fields as-is
        user_id = data["user_id"]
        game_type = data["game_type"]
        games_played = data["games_played"]
        games_won = data["games_won"]
        games_lost = data["games_lost"]
        win_percentage = data["win_percentage"]

        # Check for existing record
        stat = db.session.query(UserStat).filter_by(user_id=user_id, game_type=game_type).first()

        if stat:
            # Calculate new totals first
            total_games_played = stat.games_played + games_played
            total_games_won = stat.games_won + games_won
            total_games_lost = stat.games_lost + games_lost

            # Update fields
            stat.games_played = total_games_played
            stat.games_won = total_games_won
            stat.games_lost = total_games_lost

            # Recalculate win %
            stat.win_percentage = round((total_games_won / total_games_played) * 100, 2) if total_games_played > 0 else 0.0

        else:
            # Insert new record
            new_stat = UserStat(
                user_id=user_id,
                game_type=game_type,
                games_played=games_played,
                games_won=games_won,
                games_lost=games_lost,
                win_percentage=round((games_won / games_played) * 100, 2) if games_played > 0 else 0.0
            )
            db.session.add(new_stat)

        db.session.commit()

        flash("Tournament data uploaded successfully!", "success")
    except Exception as e:
        print("Error processing file:", e)
        flash("Failed to process the uploaded file.", "error")

    return redirect(url_for('dashboard'))