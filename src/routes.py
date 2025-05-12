from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, UserStat, Tournament, TournamentPlayer, TournamentResult, Friend, Invite
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
    my_tournaments = Tournament.query.filter_by(created_by=current_user.id).all()
    return render_template('dashboard.html',
                           tournaments=my_tournaments)

@application.route('/analytics')
@login_required
def analytics():
    user_stats = db.session.query(UserStat).filter_by(user_id=current_user.id).all()
    return render_template("analytics.html", title="Analytics", stats=user_stats)

@application.route('/requests')
@login_required
def view_requests():
    incoming = Friend.query.filter_by(
        friend_id=current_user.id
    ).all()  
    return render_template('requests.html', incoming=incoming)

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

@application.route('/search_players')
def search_players():
    """Search for players based on a query string"""
    query = request.args.get('query', '')
    
    if not query or len(query) < 1:
        return jsonify({'players': []})
    
    # Search for players matching the query in username, email, first_name, last_name, or display_name
    # Using case-insensitive search with LIKE
    search_term = f"%{query}%"
    players = User.query.filter(
        (User.username.ilike(search_term)) |
        (User.email.ilike(search_term)) |
        (User.first_name.ilike(search_term)) |
        (User.last_name.ilike(search_term)) |
        (User.display_name.ilike(search_term))
    ).limit(10).all()  # Limit to 10 results
    
    # Format the results for the frontend
    results = []
    for player in players:
        results.append({
            'id': player.id,
            'username': player.username,
            'email': player.email,
            'display_name': player.display_name,
            'first_name': player.first_name,
            'last_name': player.last_name
        })
    
    return jsonify({'players': results})

@application.route('/send_invite', methods=['POST'])
@login_required
def send_invite():
    data = request.get_json()
    recipient_id  = data.get('recipient_id')
    tournament_id = data.get('tournament_id')
    recipient = User.query.get(recipient_id)
    tournament = Tournament.query.get(tournament_id)
    if not recipient or not tournament:
        flash("Invalid user or tournament.", "error")
        return jsonify(success=True)

    exists = Invite.query.filter_by(
        recipient_id=recipient.id,
        tournament_id=tournament.id
    ).first()
    if exists:
        flash("You’ve already invited that player to this tournament.", "warning")
        return redirect(url_for('dashboard'))

    inv = Invite(
        sender_id=current_user.id,
        recipient_id=recipient.id,
        tournament_id=tournament.id
    )
    db.session.add(inv)
    db.session.commit()
    flash("Invite sent!", "success")
    return redirect(url_for('dashboard'))

@application.route('/friends/respond/<int:request_id>', methods=['POST'])
@login_required
def respond_friend_request(request_id):
    fr = Friend.query.filter_by(
        user_id=request_id,
        friend_id=current_user.id,
        status='pending'
    ).first_or_404()

    resp = request.form.get('response')
    if resp == 'accept':
        fr.status = 'accepted'
    else:  
        db.session.delete(fr)

    db.session.commit()
    return redirect(url_for('view_requests'))



@application.route('/friends/request', methods=['POST'])
@login_required
def send_friend_request():
    data = request.get_json() or {}
    friend_id = data.get('friend_id')
    if not friend_id:
        return jsonify(success=False, message="No user selected"), 400

    if User.query.get(friend_id) is None:
        return jsonify(success=False, message="User not found"), 404

    existing = Friend.query.filter_by(
        user_id=current_user.id,
        friend_id=friend_id
    ).first()
    if existing:
        return jsonify(success=False,
                       message="Already requested or you’re already friends"), 409

    fr = Friend(
        user_id=current_user.id,
        friend_id=friend_id,
        status='pending'
    )
    db.session.add(fr)
    db.session.commit()
    return jsonify(success=True)

@application.route('/friends/edit/<int:request_id>', methods=['POST'])
@login_required
def edit_friend_request(request_id):
    fr = Friend.query.filter_by(
        user_id   = request_id,
        friend_id = current_user.id
    ).first_or_404()

    fr.status = 'pending'
    db.session.commit()
    return redirect(url_for('view_requests'))
