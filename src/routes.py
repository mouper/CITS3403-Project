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

    recent = (
        db.session.query(Tournament)
        .filter_by(created_by=current_user.id)
        .order_by(Tournament.created_at.desc())
        .limit(5)
        .all()
    )

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
            name = user.username if user else player.guest_name
            standings.append({
                'username': name,
                'wins':       result.wins,
                'losses':     result.losses,
                'ties':       result.draws,
                'owp':        round(result.opponent_win_percentage * 100, 2),
                'opp_owp':    round(result.opp_opp_win_percentage  * 100, 2)
            })

        if len(standings) < 3:
            continue

        standings.sort(key=lambda x: x['wins'], reverse=True)
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
        recent_tournaments=recent_tournaments
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

        if 'title' in data:
            fmt = data['format'].strip().lower()
            allowed = {'round robin', 'swiss', 'single elimination'}
            if fmt not in allowed:
                flash(f"Invalid format '{data['format']}'. Must be one of: {', '.join(allowed)}", "error")
                return redirect(url_for('dashboard'))

            raw = data.get('round_time_minutes')
            minutes = None
            if isinstance(raw, int):
                minutes = raw
            elif isinstance(raw, str):
                m = re.search(r'\d+', raw)
                if m:
                    minutes = int(m.group())

            t = Tournament(
                title               = data['title'],
                format              = fmt,
                game_type           = data['game_type'],
                round_time_minutes  = minutes,
                created_by          = current_user.id
            )
            db.session.add(t)
            db.session.flush()

            for p in data['players']:
                tp = TournamentPlayer(
                    tournament_id = t.id,
                    guest_name    = p.get('guest_name', ''),
                    user_id       = p.get('user_id'),
                    is_confirmed  = True
                )
                db.session.add(tp)
                db.session.flush() 

                tr = TournamentResult(
                    tournament_id           = t.id,
                    player_id               = tp.id,
                    wins                    = p['wins'],
                    losses                  = p['losses'],
                    draws                   = p.get('ties', p.get('draws', 0)),
                    opponent_win_percentage = p['owp']     / 100.0,
                    opp_opp_win_percentage  = p['opp_owp'] / 100.0
                )
                db.session.add(tr)

            db.session.commit()
            flash("Tournament imported successfully!", "success")
            return redirect(url_for('dashboard'))
        
        user_id        = current_user.id
        game_type      = data['game_type']
        games_played   = data['games_played']
        games_won      = data['games_won']
        games_lost     = data['games_lost']
        win_percentage = data['win_percentage']

        stat = db.session.query(UserStat).filter_by(
            user_id=user_id, game_type=game_type
        ).first()

        if stat:
            stat.games_played   += games_played
            stat.games_won      += games_won
            stat.games_lost     += games_lost
            total = stat.games_played
            stat.win_percentage = round((stat.games_won/total)*100, 2) if total else 0.0
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

        db.session.commit()
        flash("Stats uploaded successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print("Error processing file:", e)
        flash("Failed to process the uploaded file.", "error")

    return redirect(url_for('dashboard'))