import datetime
import math
import random
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, UserStat, Tournament, TournamentPlayer, TournamentResult, Match, Round
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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
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

        if not first_name or not last_name:
            errors.append("First and last name are required.")

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('signup'))

        user = User(
            username=username,
            email=email,
            display_name=username,
            first_name=first_name,
            last_name=last_name
        )
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
        
        # Validate tournament data
        validation_result = validate_tournament_data(data)
        if not validation_result['valid']:
            return jsonify(validation_result['response']), 400
            
        # Create new tournament
        new_tournament = Tournament(
            title=data['title'],
            format=data['format'],
            game_type=data['game_type'],
            created_by=current_user.id,
            status=data['is_draft'],
            include_creator_as_player=data['include_creator_as_player']
        )
        
        # Add tournament to database and flush to get ID
        db.session.add(new_tournament)
        db.session.flush()
        
        # Process players
        for player_data in data['players']:
            new_player = create_tournament_player(new_tournament.id, player_data)
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

@application.route('/start_tournament', methods=['POST'])
@login_required
def start_tournament():
    try:
        # Get JSON data from request
        data = request.json
        
        # Validate tournament data
        validation_result = validate_tournament_data(data)
        if not validation_result['valid']:
            return jsonify(validation_result['response']), 400
            
        # Create new tournament with status='active' instead of draft
        new_tournament = Tournament(
            title=data['title'],
            format=data['format'],
            game_type=data['game_type'],
            created_by=current_user.id,
            status='active',
            include_creator_as_player=data['include_creator_as_player'],
            round_time_minutes=data.get('round_time_minutes', 30),
            num_players=len(data['players']),
            start_time=datetime.datetime.now()
        )
        
        # Calculate total_rounds based on tournament format and number of players
        player_count = len(data['players'])
        if data['format'] == 'round robin':
            new_tournament.total_rounds = player_count - 1
        elif data['format'] == 'single elimination':
            new_tournament.total_rounds = math.ceil(math.log2(player_count))
        elif data['format'] == 'swiss':
            new_tournament.total_rounds = math.ceil(math.log2(player_count))
        
        # Add tournament to database and flush to get ID
        db.session.add(new_tournament)
        db.session.flush()
        
        # Process players
        player_ids = []
        for player_data in data['players']:
            new_player = create_tournament_player(new_tournament.id, player_data)
            db.session.add(new_player)
            db.session.flush()
            player_ids.append(new_player.id)
        
        # Generate first round pairings
        if data['format'] == 'round robin' or data['format'] == 'swiss':
            # For round robin or swiss, randomly pair players for the first round
            random.shuffle(player_ids)
            
            # Create pairs
            for i in range(0, len(player_ids), 2):
                # If we have an odd number of players, the last player gets a bye
                if i + 1 >= len(player_ids):
                    # Create a bye match
                    create_match(new_tournament.id, 1, player_ids[i], None, is_bye=True)
                else:
                    # Create a normal match
                    create_match(new_tournament.id, 1, player_ids[i], player_ids[i+1])
                
        elif data['format'] == 'single elimination':
            # For single elimination, calculate number of byes needed
            next_power_of_two = 2 ** math.ceil(math.log2(len(player_ids)))
            num_byes = next_power_of_two - len(player_ids)
            
            # Shuffle players
            random.shuffle(player_ids)
            
            # Create matches with byes as needed
            match_index = 0
            for i in range(0, len(player_ids), 2):
                if match_index < num_byes:
                    # This player gets a bye
                    create_match(new_tournament.id, 1, player_ids[i], None, is_bye=True)
                    
                    # Next player also gets a match
                    if i + 1 < len(player_ids):
                        create_match(new_tournament.id, 1, player_ids[i+1], None, is_bye=True)
                else:
                    # Regular match between two players
                    if i + 1 < len(player_ids):
                        create_match(new_tournament.id, 1, player_ids[i], player_ids[i+1])
                
                match_index += 1
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tournament_id': new_tournament.id,
            'message': 'Tournament started successfully'
        })
        
    except Exception as e:
        # Roll back any changes if error occurs
        db.session.rollback()
        print(f"Error starting tournament: {str(e)}")
        
        return jsonify({
            'success': False,
            'message': f"Error starting tournament: {str(e)}"
        }), 500

@application.route('/tournament/<int:tournament_id>')
@login_required
def tournament_details(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()
    
    # Prepare matches with player details for each round
    round_matches = {}
    for round_obj in rounds:
        matches = Match.query.filter_by(round_id=round_obj.id).all()
        match_details = []
        for match in matches:
            player1 = TournamentPlayer.query.get(match.player1_id)
            player2 = TournamentPlayer.query.get(match.player2_id) if match.player2_id else None
            winner = TournamentPlayer.query.get(match.winner_id) if match.winner_id else None
            
            match_details.append({
                'match': match,
                'player1': player1,
                'player2': player2,
                'winner': winner,
                'is_bye': match.player2_id is None
            })
        
        round_matches[round_obj.round_number] = match_details
    
    return render_template('tournament.html',
                         tournament=tournament,
                         players=players,
                         rounds=rounds,
                         round_matches=round_matches)

# Helper functions
def validate_tournament_data(data):
    """Reusable validation logic with original error messages"""
    invalid_usernames = []
    email_with_accounts = []
    duplicate_usernames = []
    duplicate_emails = []
    used_usernames = {}
    used_emails = {}

    for i, player_data in enumerate(data.get('players', [])):
        # Check for duplicate usernames within the tournament
        if 'username' in player_data and player_data['username']:
            username = player_data['username'].lower()
            if username in used_usernames:
                duplicate_usernames.append(player_data['username'])
            else:
                used_usernames[username] = True
                
                # Skip validation for player 1 when it's the current user
                if not (i == 0 and data.get('include_creator_as_player', False) and 
                       player_data.get('user_id') == current_user.id):
                    # Verify username exists in the database
                    existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
                    if not existing_user:
                        invalid_usernames.append(player_data['username'])
        
        # Check for duplicate emails within the tournament
        if player_data.get('email') and player_data['email'].strip() != '':
            email = player_data['email'].lower()
            if email in used_emails:
                duplicate_emails.append(player_data['email'])
            else:
                used_emails[email] = True
                
                # Check if email is linked to TourneyPro account but "No" was selected
                if (not player_data.get('has_tourney_pro_account', True)):
                    existing_user = db.session.query(User).filter_by(email=player_data['email']).first()
                    if existing_user:
                        email_with_accounts.append(player_data['email'])
    
    # Return validation results with original error messages
    if duplicate_usernames:
        error_messages = []
        for username in duplicate_usernames:
            error_messages.append(f"Username '{username}' is used multiple times in this tournament")
            
        return {
            'valid': False,
            'response': {
                'success': False,
                'message': "Duplicate username(s) detected in tournament",
                'duplicate_usernames': duplicate_usernames,
                'detailed_errors': error_messages
            }
        }
        
    if duplicate_emails:
        error_messages = []
        for email in duplicate_emails:
            error_messages.append(f"Email '{email}' is used multiple times in this tournament")
            
        return {
            'valid': False,
            'response': {
                'success': False,
                'message': "Duplicate email(s) detected in tournament",
                'duplicate_emails': duplicate_emails,
                'detailed_errors': error_messages
            }
        }
    
    if invalid_usernames:
        error_messages = []
        for username in invalid_usernames:
            error_messages.append(f"User '{username}' does not exist")
            
        return {
            'valid': False,
            'response': {
                'success': False,
                'message': "Invalid TourneyPro username(s) detected",
                'invalid_usernames': invalid_usernames,
                'detailed_errors': error_messages
            }
        }
    
    if email_with_accounts:
        error_messages = []
        for email in email_with_accounts:
            error_messages.append(f"A TourneyPro Account has been created using the email address '{email}'")
            
        return {
            'valid': False,
            'response': {
                'success': False,
                'message': "Emails linked to existing accounts detected",
                'emails_with_accounts': email_with_accounts,
                'detailed_errors': error_messages
            }
        }

    return {'valid': True}

def create_tournament_player(tournament_id, player_data):
    """Reusable player creation logic"""
    new_player = TournamentPlayer(
        tournament_id=tournament_id,
        guest_name=player_data.get('guest_name', ''),
        email=player_data.get('email', ''),
        is_confirmed=player_data.get('is_confirmed', False)
    )

    if 'user_id' in player_data and player_data['user_id']:
        new_player.user_id = player_data['user_id']
        if player_data['user_id'] == current_user.id:
            new_player.guest_name = f"{current_user.first_name} {current_user.last_name}".strip()
    elif 'username' in player_data and player_data['username']:
        existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
        if existing_user:
            new_player.user_id = existing_user.id
            new_player.guest_name = f"{existing_user.first_name} {existing_user.last_name}".strip()
    elif player_data.get('email'):
        existing_user = db.session.query(User).filter_by(email=player_data['email']).first()
        if existing_user:
            new_player.user_id = existing_user.id
            new_player.guest_name = f"{existing_user.first_name} {existing_user.last_name}".strip()

    return new_player

def create_match(tournament_id, round_number, player1_id, player2_id=None, is_bye=False):
    """Helper to create match records with original structure"""
    # First create or get the round
    round_obj = Round.query.filter_by(
        tournament_id=tournament_id,
        round_number=round_number
    ).first()
    
    if not round_obj:
        round_obj = Round(
            tournament_id=tournament_id,
            round_number=round_number,
            status='in progress'
        )
        db.session.add(round_obj)
        db.session.flush()
    
    # Then create the match
    new_match = Match(
        round_id=round_obj.id,
        player1_id=player1_id,
        player2_id=player2_id,
        status='in progress'
    )
    db.session.add(new_match)
    return new_match

@application.route('/upload_tournament_data', methods=['POST'])
@login_required
def upload_tournament_data():
    uploaded_file = request.files.get('file')

    if not uploaded_file or not uploaded_file.filename.endswith('.json'):
        flash("Please upload a valid .json file.", "error")
        return redirect(url_for('dashboard'))

    try:
        data = json.load(uploaded_file)
        print("Parsed tournament data:", data)

        # Validate required fields
        required_keys = ["user_id", "tournament_id", "game_type", "games_won", "games_lost"]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            flash(f"Missing field(s) in upload: {', '.join(missing_keys)}", "error")
            return redirect(url_for('dashboard'))

        user_id = data["user_id"]
        tournament_id = data["tournament_id"]
        game_type = data["game_type"]
        games_won = data["games_won"]
        games_lost = data["games_lost"]
        opponent_win_percentage = data.get("opponent_win_percentage")
        opp_opp_win_percentage = data.get("opp_opp_win_percentage")

        # Calculate games_played
        games_played = games_won + games_lost

        # -------- Update UserStat --------
        stat = db.session.query(UserStat).filter_by(user_id=user_id, game_type=game_type).first()

        if stat:
            stat.games_played += games_played
            stat.games_won += games_won
            stat.games_lost += games_lost
            stat.win_percentage = round((stat.games_won / stat.games_played) * 100, 2) if stat.games_played > 0 else 0.0
        else:
            new_stat = UserStat(
                user_id=user_id,
                game_type=game_type,
                games_played=games_played,
                games_won=games_won,
                games_lost=games_lost,
                win_percentage=round((games_won / games_played) * 100, 2) if games_played > 0 else 0.0
            )
            db.session.add(new_stat)

        # -------- Add TournamentResult --------
        tournament_player = db.session.query(TournamentPlayer).filter_by(
            tournament_id=tournament_id,
            user_id=user_id
        ).first()

        if not tournament_player:
            flash("Error: User is not a participant in the given tournament.", "error")
            return redirect(url_for('dashboard'))

        # Prevent duplicate tournament results
        existing_result = db.session.query(TournamentResult).filter_by(
            tournament_id=tournament_id,
            player_id=tournament_player.id
        ).first()

        if existing_result:
            flash("Tournament result already uploaded for this user.", "error")
            return redirect(url_for('dashboard'))

        # Safe to add new result
        new_result = TournamentResult(
            tournament_id=tournament_id,
            player_id=tournament_player.id,
            game_type=game_type,
            wins=games_won,
            losses=games_lost,
            opponent_win_percentage=opponent_win_percentage,
            opp_opp_win_percentage=opp_opp_win_percentage
        )
        db.session.add(new_result)

        db.session.commit()
        flash("Tournament data uploaded successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print("Error processing file:", e)
        flash("Failed to process the uploaded file.", "error")

    return redirect(url_for('dashboard'))