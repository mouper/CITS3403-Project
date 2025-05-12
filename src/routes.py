from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import application
from models import User, UserStat, Tournament, TournamentPlayer, TournamentResult
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
    from sqlalchemy.orm import aliased
    from collections import defaultdict
    TP = aliased(TournamentPlayer)
    # ✅ 获取当前用户参与的比赛
    all_results = (
        db.session.query(TournamentResult, Tournament)
        .join(Tournament, TournamentResult.tournament_id == Tournament.id)
        .join(TP, TournamentResult.player_id == TP.id)
        .filter(TP.user_id == current_user.id)
        .all()
    )
    # ✅ 分组：wins
    grouped_results = defaultdict(list)
    for result, tournament in all_results:
        grouped_results[tournament.game_type].append((result, tournament))
    for game_type in grouped_results:
        grouped_results[game_type].sort(key=lambda x: x[0].wins, reverse=True)
    # ✅ 最近 3 场
    last_3_results = sorted(all_results, key=lambda x: x[1].created_at, reverse=True)[:3]
    # ✅ 胜率排序
    grouped_by_winrate = {}
    for game_type, entries in grouped_results.items():
        sorted_entries = sorted(
            entries,
            key=lambda x: (x[0].wins / (x[0].wins + x[0].losses)) if (x[0].wins + x[0].losses) > 0 else 0,
            reverse=True
        )
        grouped_by_winrate[game_type] = sorted_entries
    # ✅ Leaderboard 排名（综合得分）
    grouped_by_rank = {}
    for game_type, entries in grouped_results.items():
        def ranking_score(result, tournament):
            if tournament.format == "swiss":
                wr = result.wins / (result.wins + result.losses) if (result.wins + result.losses) > 0 else 0
                opwr = result.opponent_win_percentage or 0
                opowr = result.opp_opp_win_percentage or 0
                return 0.5 * wr + 0.3 * (opwr / 100) + 0.2 * (opowr / 100)
            else:
                return result.wins
        sorted_entries = sorted(
            entries,
            key=lambda x: ranking_score(x[0], x[1]),
            reverse=True
        )
        grouped_by_rank[game_type] = sorted_entries
    # ✅ 总胜率
    total_stats = (
        db.session.query(
            func.sum(TournamentResult.wins),
            func.sum(TournamentResult.losses)
        )
        .join(TP, TournamentResult.player_id == TP.id)
        .filter(TP.user_id == current_user.id)
        .first()
    )
    total_wins = total_stats[0] or 0
    total_losses = total_stats[1] or 0
    total_games = total_wins + total_losses
    total_winrate = round(total_wins / total_games * 100, 1) if total_games > 0 else 0.0
    # ✅ Admin 专属：获取自己主办的比赛及每场前三名
    hosted_tournaments = (
        db.session.query(Tournament)
        .filter_by(created_by=current_user.id)
        .order_by(Tournament.created_at.desc())
        .all()
    )
    # ✅ Admin 卡片展示：top3 玩家
    hosted_rankings_by_game = defaultdict(list)
    for tournament in hosted_tournaments:
        results = (
            db.session.query(TournamentResult, TournamentPlayer, User)
            .join(TournamentPlayer, TournamentResult.player_id == TournamentPlayer.id)
            .join(User, TournamentPlayer.user_id == User.id)
            .filter(TournamentResult.tournament_id == tournament.id)
            .all()
        )
        def rank_score(res):
            total = res.wins + res.losses
            return res.wins / total if total > 0 else 0
        top3 = sorted(results, key=lambda r: rank_score(r[0]), reverse=True)[:3]
        hosted_rankings_by_game[tournament.game_type].append({
            "tournament": tournament,
            "top3": top3
        })
    # ✅ Admin 卡片展示：所有主办比赛（用于筛选）
    hosted_by_game = defaultdict(list)
    for t in hosted_tournaments:
        hosted_by_game[t.game_type].append(t)
    hosted_game_types = list(hosted_by_game.keys())
    # ✅ 用户统计
    user_stats = db.session.query(UserStat).filter_by(user_id=current_user.id).all()
    return render_template(
        "account.html",
        title="My Account",
        results=all_results,
        grouped_results=grouped_results,
        grouped_by_winrate=grouped_by_winrate,
        grouped_by_rank=grouped_by_rank,
        user_stats=user_stats,
        total_winrate=total_winrate,
        game_types=list(grouped_results.keys()),
        last_3_results=last_3_results,
        hosted_rankings_by_game=hosted_rankings_by_game,
        hosted_game_types=hosted_game_types,
        hosted_by_game=hosted_by_game  # ✅ 新增变量，供 admin-hosted-section 使用
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
        }), 

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



import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = os.path.join("static", "uploads", "avatars")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@application.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext in ALLOWED_EXTENSIONS:
            avatar_filename = f"user_{current_user.id}.{ext}"
            file_path = os.path.join(UPLOAD_FOLDER, avatar_filename)
            file.save(file_path)
            current_user.avatar_path = f"uploads/avatars/{avatar_filename}"
            db.session.commit()
            flash("Avatar updated successfully!", "success")
        else:
            flash("Invalid file type. Please upload an image.", "error")
    else:
        flash("No file selected.", "error")
    return redirect(url_for('account'))

@application.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    if email:
        current_user.email = email
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name

    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('account'))


