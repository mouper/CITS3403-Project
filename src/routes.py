from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from src.app import application
from models import db, User, Tournament, UserStat, TournamentResult
from db import db  # Use the centralized db object from db.py
from sqlalchemy import func
import json
from datetime import datetime

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
    # 查询该用户所有比赛结果及对应比赛
    all_results = (
        db.session.query(TournamentResult, Tournament)
        .join(Tournament, TournamentResult.tournament_id == Tournament.id)
        .filter(TournamentResult.player_id == current_user.id)
        .all()
    )

    # 将比赛结果按 game_type 分组，并按 wins 排序
    from collections import defaultdict
    grouped_results = defaultdict(list)

    for result, tournament in all_results:
        grouped_results[tournament.game_type].append((result, tournament))

    for game_type in grouped_results:
        grouped_results[game_type].sort(key=lambda x: x[0].wins, reverse=True)

    # routes.py -> /account 视图中添加这段
    last_3_results = sorted(all_results, key=lambda x: x[1].created_at, reverse=True)[:3]

    # 生成游戏类型列表供下拉菜单使用
    game_types = list(grouped_results.keys())

    # 获取统计数据
    user_stats = db.session.query(UserStat).filter_by(user_id=current_user.id).all()

    # 按 winrate 排序 (wins / total)
    grouped_by_winrate = {}
    for game_type, entries in grouped_results.items():
        sorted_entries = sorted(
            entries,
            key=lambda x: (x[0].wins / (x[0].wins + x[0].losses)) if (x[0].wins + x[0].losses) > 0 else 0,
            reverse=True
        )
        grouped_by_winrate[game_type] = sorted_entries

    total_stats = (
        db.session.query(
            func.sum(TournamentResult.wins),
            func.sum(TournamentResult.losses)
        )
        .filter(TournamentResult.player_id == current_user.id)
        .first()
    )

    total_wins = total_stats[0] or 0
    total_losses = total_stats[1] or 0
    total_games = total_wins + total_losses
    total_winrate = round(total_wins / total_games * 100, 1) if total_games > 0 else 0.0

    return render_template(
        "account.html",
        title="My Account",
        results=all_results,  # 如果 html 用不到就可以删掉
        grouped_results=grouped_results,
        grouped_by_winrate=grouped_by_winrate,  
        user_stats=user_stats,
        total_winrate=total_winrate,
        game_types=game_types,
        last_3_results=last_3_results
    )

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

        # ✅ 支持两种格式：单个 tournament 或多个 tournaments
        tournaments = data.get("tournaments", [data])

        for entry in tournaments:
            game_type = entry["game_type"]
            games_played = entry["games_played"]
            games_won = entry["games_won"]
            games_lost = entry["games_lost"]
            opponent_win_percentage = entry.get("opponent_win_percentage", 0.0)
            opp_opp_win_percentage = entry.get("opp_opp_win_percentage", 0.0)
            win_percentage = round((games_won / games_played) * 100, 2) if games_played > 0 else 0.0

            # ✅ Step 1: Update or Insert UserStat
            stat = db.session.query(UserStat).filter_by(user_id=current_user.id, game_type=game_type).first()

            if stat:
                stat.games_played += games_played
                stat.games_won += games_won
                stat.games_lost += games_lost
                stat.win_percentage = round((stat.games_won / stat.games_played) * 100, 2) if stat.games_played > 0 else 0.0
            else:
                stat = UserStat(
                    user_id=current_user.id,
                    game_type=game_type,
                    games_played=games_played,
                    games_won=games_won,
                    games_lost=games_lost,
                    win_percentage=win_percentage
                )
                db.session.add(stat)

            # ✅ Step 2: Insert Tournament
            tournament = Tournament(
                title=entry["title"],
                format=entry["format"],
                game_type=game_type,
                status=entry["status"],
                num_players=entry["num_players"],
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(tournament)
            db.session.flush()  # Get tournament.id

            # ✅ Step 3: Insert TournamentResult
            result = TournamentResult(
                tournament_id=tournament.id,
                player_id=current_user.id,
                wins=games_won,
                losses=games_lost,
                opponent_win_percentage=opponent_win_percentage,
                opp_opp_win_percentage=opp_opp_win_percentage
            )
            db.session.add(result)

        db.session.commit()
        flash("Tournaments uploaded successfully!", "success")

    except Exception as e:
        db.session.rollback()
        print("Upload error:", e)
        flash("Upload failed!", "error")

    return redirect(url_for('dashboard'))
