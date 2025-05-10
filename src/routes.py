from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, UserStat, Tournament, TournamentPlayer, TournamentResult
from db import db  # Use the centralized db object from db.py
import json
import re

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

    limit_param = request.args.get('limit', 'all')
    try:
        limit = int(limit_param)
    except ValueError:
        limit = None  # means “all”

    base_q = (
        db.session.query(Tournament)
        .filter_by(created_by=current_user.id)
        .order_by(Tournament.created_at.desc())
    )

    if limit:
        recent = base_q.limit(limit).all()
    else:
        recent = base_q.all()

    recent_tournaments = []
    for tourney in recent:
        rows = (
            db.session.query(TournamentPlayer, TournamentResult, User)
            .join(TournamentResult, TournamentResult.player_id == TournamentPlayer.id)
            .outerjoin(User, TournamentPlayer.user_id == User.id)
            .filter(TournamentPlayer.tournament_id == tourney.id)
            .all()
        )

        standings = []
        for player, result, user in rows:
            if player.user_id == 1:
                name = player.guest_name
            else:
                name = user.username if user else player.guest_name
            standings.append({
                'username': name,
                'wins':       result.wins,
                'losses':     result.losses,
                'owp':        round(result.opponent_win_percentage * 100, 2),
                'opp_owp':    round(result.opp_opp_win_percentage  * 100, 2)
            })

        if len(standings) < 3:
            continue

        standings.sort(key=lambda p: (p['wins'], p['opp_owp']),reverse=True)
        recent_tournaments.append({
            'id':                   tourney.id,
            'title':                tourney.title,
            'format':               tourney.format,
            'game_type':            tourney.game_type,
            'round_time_minutes':   tourney.round_time_minutes,
            'date':                 tourney.created_at.strftime("%d/%m/%Y"),
            'standings':            standings
        })

    return render_template(
        'analytics.html',
        title='Analytics',
        stats=user_stats,
        recent_tournaments=recent_tournaments,
        limit=limit_param
    )

    
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
        data = request.json
        invalid_usernames = []
        for i, player_data in enumerate(data.get('players', [])):
            if 'username' in player_data and player_data['username'] and not (
                i == 0 and data.get('include_creator_as_player', False) and 
                player_data.get('user_id') == current_user.id
            ):
                existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
                if not existing_user:
                    invalid_usernames.append(player_data['username'])
                    
        if invalid_usernames:
            return jsonify({
                'success': False,
                'message': f"Invalid TourneyPro username(s): {', '.join(invalid_usernames)}",
                'invalid_usernames': invalid_usernames
            }), 400
            
        new_tournament = Tournament(
            title=data['title'],
            format=data['format'],
            game_type=data['game_type'],
            created_by=current_user.id,
            is_draft=data['is_draft'],
            include_creator_as_player=data['include_creator_as_player']
        )
        
        db.session.add(new_tournament)
        db.session.flush()
        
        for player_data in data['players']:
            new_player = TournamentPlayer(
                tournament_id=new_tournament.id,
                guest_name=player_data.get('guest_name', ''),
                email=player_data.get('email', ''),
                is_confirmed=player_data.get('is_confirmed', False)
            )
            
            if 'user_id' in player_data and player_data['user_id']:
                new_player.user_id = player_data['user_id']
            elif 'username' in player_data and player_data['username']:
                existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
                if existing_user:
                    new_player.user_id = existing_user.id
            elif player_data.get('email'):
                existing_user = db.session.query(User).filter_by(email=player_data['email']).first()
                if existing_user:
                    new_player.user_id = existing_user.id
            
            db.session.add(new_player)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tournament_id': new_tournament.id,
            'message': 'Tournament saved successfully'
        })
        
    except Exception as e:
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
                user_id       = current_user.id,
                game_type     = game_type,
                games_played  = games_played,
                games_won     = games_won,
                games_lost    = games_lost,
                win_percentage= win_percentage
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