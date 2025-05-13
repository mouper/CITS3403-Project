import datetime
import math
import random
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from app import application, mail
from models import Friend, User, UserStat, Tournament, TournamentPlayer, TournamentResult, Match, Round, Friend, Invite
from db import db  # Use the centralized db object from db.py
import json, io
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
    my_tournaments = Tournament.query.filter_by(created_by=current_user.id).all()

    sent_accepted = Friend.query.filter_by(user_id=current_user.id, status='accepted').all()
    recv_accepted = Friend.query.filter_by(friend_id=current_user.id, status='accepted').all()

    accepted_friends = [f.recipient for f in sent_accepted] + [f.sender for f in recv_accepted]

    accepted_friend_usernames = [friend.username for friend in accepted_friends]

    return render_template(
        'dashboard.html',
        tournaments=my_tournaments,
        accepted_friend_usernames=accepted_friend_usernames
    )

    
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
            if user:
                display_name = user.display_name
            else:
                first = player.guest_firstname or ""
                last_initial = player.guest_lastname[0] if player.guest_lastname else ""
                display_name = f"{first} {last_initial}".strip() or "Unknown"

            standings.append({
                'username': display_name,
                'wins':     result.wins,
                'losses':   result.losses,
                'owp':      round(result.opponent_win_percentage * 100, 2),
                'opp_owp':  round(result.opp_opp_win_percentage   * 100, 2)
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
def view_requests():
    incoming_rels = Friend.query.filter_by(friend_id=current_user.id).all()

    incoming = [
        { "fr": fr, "user": fr.sender }
        for fr in incoming_rels
    ]

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
        data = request.json
        
        # Validate tournament data
        validation_result = validate_tournament_data(data)
        if not validation_result['valid']:
            return jsonify(validation_result['response']), 400
            
        new_tournament = Tournament(
            title=data['title'],
            format=data['format'],
            game_type=data['game_type'],
            created_by=current_user.id,
            status=data['is_draft'],
            include_creator_as_player=data['include_creator_as_player']
        )
        
        db.session.add(new_tournament)
        db.session.flush()
        
        for player_data in data['players']:
            new_player = create_tournament_player(new_tournament.id, player_data)
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
                    create_match(new_tournament.id, 1, player_ids[i], None, is_bye=True, status='not started')
                else:
                    # Create a normal match
                    create_match(new_tournament.id, 1, player_ids[i], player_ids[i+1], status='not started')
                
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
                    create_match(new_tournament.id, 1, player_ids[i], None, is_bye=True, status='not started')
                    
                    # Next player also gets a match
                    if i + 1 < len(player_ids):
                        create_match(new_tournament.id, 1, player_ids[i+1], None, is_bye=True, status='not started')
                else:
                    # Regular match between two players
                    if i + 1 < len(player_ids):
                        create_match(new_tournament.id, 1, player_ids[i], player_ids[i+1], status='not started')
                
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
    
@application.route('/tournament/<int:tournament_id>', methods=['GET'])
@login_required
def view_tournament(tournament_id):
    view_state = request.args.get('view_state', 'normal')
    # Get the tournament
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get all rounds for this tournament
    rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()
    rounds_count = len(rounds)
    completed_rounds = sum(1 for r in rounds if r.status == 'completed')
    
    # Get current round (the first non-completed round, or the last round if all are completed)
    current_round = next((r for r in rounds if r.status != 'completed'), rounds[-1] if rounds else None)
    
    # Get all players in this tournament
    tournament_players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    
    # Create a dictionary to easily access players by ID
    players = {}
    for player in tournament_players:
        players[player.id] = player
        # Eagerly load user data if player is a registered user
        if player.user_id:
            player.user = User.query.get(player.user_id)
    
    # Get all matches organized by round
    matches_by_round = {}
    all_matches = Match.query.join(Round).filter(Round.tournament_id == tournament_id).all()
    
    for match in all_matches:
        round_obj = Round.query.get(match.round_id)
        round_num = round_obj.round_number
        if round_num not in matches_by_round:
            matches_by_round[round_num] = []
        matches_by_round[round_num].append(match)
    
    # Get current round matches
    current_matches = []
    if current_round:
        current_matches = Match.query.filter_by(round_id=current_round.id).all()
    
    # Calculate player stats (wins/losses across all completed rounds)
    player_stats = {}
    for player in tournament_players:
        player_stats[player.id] = {'wins': 0, 'losses': 0}
    
    for match in all_matches:
        if match.winner_id:
            # Increment winner's win count
            if match.winner_id in player_stats:
                player_stats[match.winner_id]['wins'] += 1
            
            # Increment loser's loss count
            if match.player1_id != match.winner_id and match.player1_id in player_stats:
                player_stats[match.player1_id]['losses'] += 1
            
            if match.player2_id and match.player2_id != match.winner_id and match.player2_id in player_stats:
                player_stats[match.player2_id]['losses'] += 1
    
    # Prepare player results for rankings
    ranked_players = []
    for player_id, player in players.items():
        player_result = {
            'id': player_id,
            'name': "",
            'wins': player_stats[player_id]['wins'],
            'losses': player_stats[player_id]['losses'],
            'owp': 0,
            'oowp': 0
        }
        
        # Set player name
        if player.user_id:
            player_result['name'] = player.user.display_name or player.user.username
        else:
            player_result['name'] = f"{player.guest_firstname} {player.guest_lastname}"
        
        # Get tournament result for this player (for Swiss tiebreakers)
        tournament_result = TournamentResult.query.filter_by(
            tournament_id=tournament_id, 
            player_id=player_id
        ).first()
        
        if tournament_result:
            player_result['owp'] = tournament_result.opponent_win_percentage or 0
            player_result['oowp'] = tournament_result.opp_opp_win_percentage or 0
        
        ranked_players.append(player_result)
    
    # Sort ranked players based on tournament format
    if tournament.format == 'swiss':
        ranked_players.sort(key=lambda x: (-x['wins'], -x['owp'], -x['oowp']))
    else:
        ranked_players.sort(key=lambda x: -x['wins'])
    
    # If tournament is completed, use the completed template with special stats
    if tournament.status == 'completed':
        # Calculate additional tournament statistics
        total_matches = sum(len(matches) for matches in matches_by_round.values())
        total_byes = sum(1 for match in all_matches if match.is_bye)
        
        # Calculate tournament duration
        if tournament.start_time:
            end_time = datetime.datetime.now()
            duration = end_time - tournament.start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            tournament_duration = f"{int(hours)}h {int(minutes)}m"
        else:
            tournament_duration = "N/A"
        
        # Check if current user is the tournament creator
        is_creator = current_user.id == tournament.created_by
        
        return render_template(
            'tournament_completed.html',
            tournament=tournament,
            rounds=rounds,
            rounds_count=rounds_count,
            completed_rounds=completed_rounds,
            players=players,
            matches_by_round=matches_by_round,
            player_stats=player_stats,
            ranked_players=ranked_players,
            player_count=len(tournament_players),
            total_matches=total_matches,
            total_byes=total_byes,
            tournament_duration=tournament_duration,
            is_creator=is_creator
        )
    else:
        # Use the regular tournament template for in-progress tournaments
        return render_template(
            'tournament.html',
            tournament=tournament,
            rounds=rounds,
            rounds_count=rounds_count,
            completed_rounds=completed_rounds,
            current_round=current_round,
            players=players,
            matches_by_round=matches_by_round,
            current_matches=current_matches,
            player_stats=player_stats,
            ranked_players=ranked_players,
            view_state=view_state
        )
    
@application.route('/tournament/<int:tournament_id>/completed', methods=['GET'])
@login_required
def view_tournament_completed(tournament_id):
    # Mark tournament as completed if it's not already
    tournament = Tournament.query.get_or_404(tournament_id)
    if tournament.status != 'completed':
        tournament.status = 'completed'
        db.session.commit()
    
    # Redirect to the main tournament view, which will now render the completed template
    return redirect(url_for('view_tournament', tournament_id=tournament_id))

@application.route('/tournament/<int:tournament_id>/start_round', methods=['POST'])
@login_required
def start_round(tournament_id):
    """Start a round in the tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get the current round (first non-completed round)
    rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()
    current_round = next((r for r in rounds if r.status != 'completed'), None)
    
    if not current_round:
        # If all rounds are completed, create a new one only if we're under the total rounds limit
        completed_rounds = len(rounds)
        if completed_rounds < tournament.total_rounds:
            current_round = Round(
                tournament_id=tournament_id,
                round_number=completed_rounds + 1,
                status='not started'
            )
            db.session.add(current_round)
            db.session.commit()
        else:
            return jsonify(success=False, message="All rounds have been completed"), 400
    
    # Change status to 'in progress' if not already
    if current_round.status == 'not started':
        current_round.status = 'in progress'
        db.session.commit()
        
    return jsonify(success=True)


@application.route('/tournament/<int:tournament_id>/complete_round', methods=['POST'])
@login_required
def complete_round(tournament_id):
    """Complete the current round and save match results."""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get the current round
    current_round = Round.query.filter_by(
        tournament_id=tournament_id, 
        status='in progress'
    ).first()
    
    if not current_round:
        return jsonify(success=False, message="No round in progress"), 400
    
    # Get match results from request
    match_results = request.json.get('match_results', [])
    
    # Get all matches for this round to validate completeness
    all_matches = Match.query.filter_by(round_id=current_round.id).all()
    non_bye_matches = [m for m in all_matches if not m.is_bye]
    
    # Check if all non-bye matches have a result
    if len(match_results) < len(non_bye_matches):
        return jsonify(success=False, message="Not all matches have results"), 400
    
    # Update match results
    for result in match_results:
        match_id = result.get('match_id')
        winner_id = result.get('winner_id')
        
        match = Match.query.get(match_id)
        if match and match.round_id == current_round.id:
            match.winner_id = winner_id
            match.status = 'completed'
    
    # Mark round as completed
    current_round.status = 'completed'
    db.session.commit()
    
    # Update tournament results and tiebreakers
    update_tournament_results(tournament_id)
    
    return jsonify(success=True)



@application.route('/tournament/<int:tournament_id>/save_results', methods=['POST'])
@login_required
def save_results(tournament_id):
    """Save match results without completing the round."""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get match results from request
    match_results = request.json.get('match_results', [])
    
    # Update match results
    for result in match_results:
        match_id = result.get('match_id')
        winner_id = result.get('winner_id')
        
        match = Match.query.get(match_id)
        if match:
            match.winner_id = winner_id
    
    db.session.commit()
    return jsonify(success=True)


@application.route('/tournament/<int:tournament_id>/next_round', methods=['POST'])
@login_required
def next_round(tournament_id):
    """Create the next round for the tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)
    
    # Get the current round
    current_round = Round.query.filter_by(
        tournament_id=tournament_id, 
        status='completed'
    ).order_by(Round.round_number.desc()).first()
    
    if not current_round:
        return jsonify(success=False, message="No completed round found"), 400
    
    # Verify all matches in the current round have winners
    incomplete_matches = Match.query.filter_by(
        round_id=current_round.id,
        winner_id=None,
        is_bye=False
    ).count()
    
    if incomplete_matches > 0:
        return jsonify(success=False, message="Not all matches have been completed"), 400
    
    # Get all rounds for this tournament
    rounds = Round.query.filter_by(tournament_id=tournament_id).order_by(Round.round_number).all()
    completed_rounds = sum(1 for r in rounds if r.status == 'completed')
    
    if completed_rounds >= tournament.total_rounds:
        # All rounds are completed, mark the tournament as finished
        tournament.status = 'completed'
        db.session.commit()
        return jsonify(success=True)
    
    # Create the next round
    next_round_number = completed_rounds + 1
    new_round = Round(
        tournament_id=tournament_id,
        round_number=next_round_number,
        status='not started'
    )
    db.session.add(new_round)
    db.session.commit()
    
    # Create match pairings for the new round
    create_pairings_for_round(tournament, new_round)
    
    return jsonify(success=True)

@application.route('/tournament/<int:tournament_id>/send_results', methods=['POST'])
@login_required
def send_results_to_players(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()

    ranked_players = compute_rankings(tournament_id, tournament.format)
    total_matches = Match.query.join(Round, Match.round_id == Round.id).filter(Round.tournament_id == tournament.id).count()
    total_byes = Match.query.join(Round, Match.round_id == Round.id).filter(
        Round.tournament_id == tournament.id,
        Match.is_bye == True
    ).count()

    for player in players:
        if not player.email:
            continue

        html_body = render_template(
            "components/tournament_results_email.html",
            tournament=tournament,
            ranked_players=ranked_players,
            total_matches=total_matches,
            total_byes=total_byes
        )

        msg = Message(subject=f"Tournament Results: {tournament.title}",
                      recipients=[player.email])
        msg.html = html_body

        # Guest attachment
        if not player.user_id:
            player_matches = Match.query.join(Round, Match.round_id == Round.id).filter(
                ((Match.player1_id == player.id) | (Match.player2_id == player.id)) &
                (Round.tournament_id == tournament.id)
            ).all()

            wins = sum(1 for m in player_matches if m.winner_id == player.id)
            losses = sum(1 for m in player_matches if m.winner_id and m.winner_id != player.id)

            result = {
                "user_id": None,
                "tournament_id": tournament_id,
                "game_type": tournament.game_type,
                "games_won": wins,
                "games_lost": losses,
                "opponent_win_percentage": None,
                "opp_opp_win_percentage": None
            }

            buffer = io.BytesIO()
            buffer.write(json.dumps(result).encode('utf-8'))
            buffer.seek(0)
            msg.attach(f"tournament_{tournament_id}_results.json", "application/json", buffer.read())

        mail.send(msg)

    flash("Results sent to all players!", "success")
    return redirect(url_for('dashboard'))

def compute_rankings(tournament_id, format):
    # Get all tournament players
    players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()

    # Initialize stats for each player
    player_stats = {p.id: {"player": p, "wins": 0, "losses": 0, "opponents": []} for p in players}

    # Get the matches for this tournament
    matches = Match.query.join(Round, Match.round_id == Round.id)\
        .filter(Round.tournament_id == tournament_id).all()

    # Process each match
    for match in matches:
        p1 = match.player1_id
        p2 = match.player2_id
        winner = match.winner_id

        # Handle bye: Player2 is None, meaning player 1 got a bye
        if match.is_bye:
            if p1:
                # Player 1 gets the win
                player_stats[p1]["wins"] += 1
                player_stats[p1]["opponents"].append(None)  # No opponent for player1 in bye
            if p2:
                # Player 2 got a bye, they don't get the loss
                player_stats[p2]["wins"] += 1
                player_stats[p2]["opponents"].append(None)  # No opponent for player2 in bye
            continue

        # Track the players' opponents if it's a real match (i.e., no bye)
        if p1 and p2:  # Ensure both players exist
            player_stats[p1]["opponents"].append(p2)
            player_stats[p2]["opponents"].append(p1)

        # Track wins and losses
        if winner == p1:
            player_stats[p1]["wins"] += 1
            if p2:
                player_stats[p2]["losses"] += 1
        elif winner == p2:
            player_stats[p2]["wins"] += 1
            player_stats[p1]["losses"] += 1

    # Calculate OWP (Opponent Win Percentage) and OOWP (Opponents' Opponent Win Percentage)
    standings = []

    for player_id, stats in player_stats.items():
        opponents = stats["opponents"]
        opp_wp_list = []

        # Calculate OWP: Average win percentage of the player's opponents
        for opp_id in opponents:
            if opp_id:  # Skip None (bye)
                opp_results = TournamentResult.query.filter_by(player_id=opp_id, tournament_id=tournament_id).first()
                if opp_results:
                    total_games = opp_results.wins + opp_results.losses
                    if total_games > 0:
                        opp_wp_list.append(opp_results.wins / total_games)

        owp = sum(opp_wp_list) / len(opp_wp_list) if opp_wp_list else 0

        # Calculate OOWP: Average OWP of the player's opponents
        oowp_list = []
        for opp_id in opponents:
            if opp_id:  # Skip None (bye)
                opp_results = TournamentResult.query.filter_by(player_id=opp_id, tournament_id=tournament_id).first()
                if opp_results:
                    oowp_list.append(opp_results.opponent_win_percentage or 0)

        oowp = sum(oowp_list) / len(oowp_list) if oowp_list else 0

        # Add player's data to the standings
        p = stats["player"]
        
        # Use the guest's name if user_id is None
        if p.user_id:
            user = User.query.get(p.user_id)
            player_name = f"{user.first_name} {user.last_name}" if user else f"{p.guest_firstname} {p.guest_lastname}"
        else:
            player_name = f"{p.guest_firstname} {p.guest_lastname}"

        standings.append({
            "name": player_name,
            "wins": stats["wins"],
            "losses": stats["losses"],
            "owp": round(owp, 3),
            "oowp": round(oowp, 3)
        })

    # Sort the standings: by wins, then OWP, then OOWP
    standings.sort(key=lambda x: (-x["wins"], -x["owp"], -x["oowp"]))

    return standings


def create_pairings_for_round(tournament, current_round):
    """Create match pairings for the current round based on tournament format."""
    tournament_players = TournamentPlayer.query.filter_by(tournament_id=tournament.id).all()
    
    if tournament.format == 'swiss':
        create_swiss_pairings(tournament, current_round, tournament_players)
    elif tournament.format == 'single elimination':
        create_single_elimination_pairings(tournament, current_round, tournament_players)
    elif tournament.format == 'round robin':
        create_round_robin_pairings(tournament, current_round, tournament_players)
    
    db.session.commit()


def create_swiss_pairings(tournament, current_round, players):
    """Create pairings for Swiss tournament format."""
    # Get player standings based on wins and tiebreakers
    player_standings = []
    
    for player in players:
        # Get player's tournament result
        result = TournamentResult.query.filter_by(
            tournament_id=tournament.id,
            player_id=player.id
        ).first()
        
        if not result:
            result = TournamentResult(
                tournament_id=tournament.id,
                player_id=player.id,
                game_type=tournament.game_type,
                wins=0,
                losses=0,
                opponent_win_percentage=0.0,
                opp_opp_win_percentage=0.0
            )
            db.session.add(result)
        
        player_standings.append({
            'player_id': player.id,
            'wins': result.wins,
            'losses': result.losses,
            'owp': result.opponent_win_percentage or 0.0,
            'oowp': result.opp_opp_win_percentage or 0.0,
            'paired': False  # Flag to track if player has been paired in this round
        })
    
    # Sort by score (wins), then by tiebreakers
    player_standings.sort(key=lambda x: (-x['wins'], -x['owp'], -x['oowp']))
    
    # Get previously paired opponents to avoid re-pairing
    previous_pairings = set()
    previous_rounds = Round.query.filter(
        Round.tournament_id == tournament.id,
        Round.round_number < current_round.round_number
    ).all()
    
    for round_obj in previous_rounds:
        matches = Match.query.filter_by(round_id=round_obj.id).all()
        for match in matches:
            if match.player1_id and match.player2_id:
                pair = tuple(sorted([match.player1_id, match.player2_id]))
                previous_pairings.add(pair)
    
    # Create pairings for the current round
    matches = []
    
    # Pair players with the same score as much as possible
    score_groups = {}
    for player in player_standings:
        score = player['wins']
        if score not in score_groups:
            score_groups[score] = []
        score_groups[score].append(player)
    
    # Process each score group
    for score in sorted(score_groups.keys(), reverse=True):
        players_group = score_groups[score]
        
        while len(players_group) > 1:
            player1 = players_group[0]
            players_group.pop(0)
            
            # Try to find an opponent not previously paired with player1
            paired = False
            for i, player2 in enumerate(players_group):
                pair = tuple(sorted([player1['player_id'], player2['player_id']]))
                if pair not in previous_pairings:
                    matches.append((player1['player_id'], player2['player_id']))
                    players_group.pop(i)
                    paired = True
                    break
            
            # If no unpaired opponent found, pair with the first available
            if not paired and players_group:
                player2 = players_group[0]
                players_group.pop(0)
                matches.append((player1['player_id'], player2['player_id']))
    
    # Handle odd number of players with a bye
    remaining_players = []
    for score in sorted(score_groups.keys(), reverse=True):
        remaining_players.extend(score_groups[score])
    
    if remaining_players:
        # Give bye to the lowest-ranked player who hasn't had a bye yet
        player_with_bye = remaining_players[-1]['player_id']
        
        # Check if this player already had a bye
        had_bye = Match.query.join(Round).filter(
            Round.tournament_id == tournament.id,
            Match.player1_id == player_with_bye,
            Match.is_bye == True
        ).first()
        
        if had_bye:
            # Try to find someone else for the bye
            for player in reversed(player_standings):
                if player['player_id'] != player_with_bye:
                    had_bye = Match.query.join(Round).filter(
                        Round.tournament_id == tournament.id,
                        Match.player1_id == player['player_id'],
                        Match.is_bye == True
                    ).first()
                    
                    if not had_bye:
                        player_with_bye = player['player_id']
                        break
        
        # Create a bye match
        bye_match = Match(
            round_id=current_round.id,
            player1_id=player_with_bye,
            player2_id=None,
            is_bye=True,
            status='not started'
        )
        db.session.add(bye_match)
    
    # Create matches in the database
    for player1_id, player2_id in matches:
        match = Match(
            round_id=current_round.id,
            player1_id=player1_id,
            player2_id=player2_id,
            is_bye=False,
            status='not started'
        )
        db.session.add(match)


def create_single_elimination_pairings(tournament, current_round, players):
    """Create pairings for single elimination tournament format."""
    # For first round: random seeding
    if current_round.round_number == 1:
        import random
        player_ids = [p.id for p in players]
        random.shuffle(player_ids)
        
        # Add byes for power of 2
        next_power_of_2 = 2 ** (tournament.total_rounds)
        while len(player_ids) < next_power_of_2:
            player_ids.append(None)  # None represents a bye
        
        # Create first round matches
        for i in range(0, len(player_ids), 2):
            player1_id = player_ids[i]
            player2_id = player_ids[i+1] if i+1 < len(player_ids) else None
            
            is_bye = player2_id is None
            
            match = Match(
                round_id=current_round.id,
                player1_id=player1_id,
                player2_id=player2_id,
                is_bye=is_bye,
                status='not started'
            )
            db.session.add(match)
    else:
        # For subsequent rounds: winners of previous round
        prev_round = Round.query.filter_by(
            tournament_id=tournament.id,
            round_number=current_round.round_number - 1
        ).first()
        
        prev_matches = Match.query.filter_by(round_id=prev_round.id).order_by(Match.id).all()
        
        # Create matches based on winners from previous round
        for i in range(0, len(prev_matches), 2):
            match1 = prev_matches[i]
            match2 = prev_matches[i+1] if i+1 < len(prev_matches) else None
            
            player1_id = match1.winner_id if match1 and match1.winner_id else None
            player2_id = match2.winner_id if match2 and match2.winner_id else None
            
            is_bye = player2_id is None and player1_id is not None
            
            match = Match(
                round_id=current_round.id,
                player1_id=player1_id,
                player2_id=player2_id,
                is_bye=is_bye,
                status='not started'
            )
            db.session.add(match)


def create_round_robin_pairings(tournament, current_round, players):
    """Create pairings for round robin tournament format."""
    player_ids = [p.id for p in players]
    n = len(player_ids)
    
    # Handle odd number of players
    has_bye = False
    if n % 2 != 0:
        player_ids.append(None)  # Add a bye
        n += 1
        has_bye = True
    
    round_num = current_round.round_number
    
    pairings = []
    
    if round_num <= n - 1:
        fixed = player_ids[0]
        rotating = player_ids[1:]
        
        rotation = (round_num - 1) % (n - 1)
        rotated = rotating[-rotation:] + rotating[:-rotation]
        
        for i in range(n // 2):
            if i == 0:
                p1, p2 = fixed, rotated[i]
            else:
                p1, p2 = rotated[i], rotated[n - 1 - i]
            
            # Ensure player1_id is always not None
            if p1 is None and p2 is not None:
                p1, p2 = p2, None
            elif p1 is None and p2 is None:
                continue  # Skip invalid pairing (shouldn't occur, but safe check)

            pairings.append((p1, p2))
    
    # Create matches in the database
    for player1_id, player2_id in pairings:
        is_bye = player2_id is None
        
        match = Match(
            round_id=current_round.id,
            player1_id=player1_id,
            player2_id=player2_id,
            is_bye=is_bye,
            status='not started'
        )
        db.session.add(match)


def update_tournament_results(tournament_id):
    """Update tournament results and tiebreakers after a round is completed."""
    tournament = Tournament.query.get(tournament_id)
    
    # Get all players in this tournament
    players = TournamentPlayer.query.filter_by(tournament_id=tournament_id).all()
    
    # Get all matches across all rounds
    matches = Match.query.join(Round).filter(
        Round.tournament_id == tournament_id,
        Round.status == 'completed'
    ).all()
    
    # Calculate win-loss record for each player
    player_records = {}
    for player in players:
        player_records[player.id] = {
            'player_id': player.id,
            'wins': 0,
            'losses': 0,
            'opponents': []  # To track opponents for tiebreakers
        }
    
    # Process match results
    for match in matches:
        if match.winner_id:
            # Record the win
            if match.winner_id in player_records:
                player_records[match.winner_id]['wins'] += 1
            
            # Record the loss for the other player
            if match.player1_id != match.winner_id and match.player1_id in player_records:
                player_records[match.player1_id]['losses'] += 1
                # Add opponent for tiebreakers
                if not match.is_bye and match.player2_id:
                    player_records[match.player1_id]['opponents'].append(match.player2_id)
            
            if match.player2_id and match.player2_id != match.winner_id and match.player2_id in player_records:
                player_records[match.player2_id]['losses'] += 1
                # Add opponent for tiebreakers
                player_records[match.player2_id]['opponents'].append(match.player1_id)
    
    # Calculate opponent win percentage (OWP) for Swiss tiebreakers
    if tournament.format == 'swiss':
        for player_id, record in player_records.items():
            opponents = record['opponents']
            if not opponents:
                record['owp'] = 0.0
                continue
            
            # Calculate opponents' win percentages
            opponent_win_percentages = []
            for opp_id in opponents:
                if opp_id in player_records:
                    opp_record = player_records[opp_id]
                    # Exclude matches against this player for opponent's win percentage
                    opp_wins = opp_record['wins']
                    opp_losses = opp_record['losses']
                    
                    # Handle division by zero
                    if opp_wins + opp_losses > 0:
                        opp_win_pct = opp_wins / (opp_wins + opp_losses)
                    else:
                        opp_win_pct = 0.0
                    
                    opponent_win_percentages.append(opp_win_pct)
            
            # Calculate average opponent win percentage
            if opponent_win_percentages:
                record['owp'] = sum(opponent_win_percentages) / len(opponent_win_percentages)
            else:
                record['owp'] = 0.0
        
        # Calculate opponents' opponent win percentage (OOWP)
        for player_id, record in player_records.items():
            opponents = record['opponents']
            if not opponents:
                record['oowp'] = 0.0
                continue
            
            opp_opp_win_percentages = []
            for opp_id in opponents:
                if opp_id in player_records and 'owp' in player_records[opp_id]:
                    opp_opp_win_percentages.append(player_records[opp_id]['owp'])
            
            if opp_opp_win_percentages:
                record['oowp'] = sum(opp_opp_win_percentages) / len(opp_opp_win_percentages)
            else:
                record['oowp'] = 0.0
    
    # Update tournament results in the database
    for player_id, record in player_records.items():
        result = TournamentResult.query.filter_by(
            tournament_id=tournament_id,
            player_id=player_id
        ).first()
        
        if not result:
            result = TournamentResult(
                tournament_id=tournament_id,
                player_id=player_id,
                game_type=tournament.game_type
            )
            db.session.add(result)
        
        result.wins = record['wins']
        result.losses = record['losses']
        
        if tournament.format == 'swiss':
            result.opponent_win_percentage = record.get('owp', 0.0)
            result.opp_opp_win_percentage = record.get('oowp', 0.0)
    
    db.session.commit()

# Helper functions
def validate_tournament_data(data):
    """Reusable validation logic with original error messages"""
    invalid_usernames = []
    email_with_accounts = []
    duplicate_usernames = []
    duplicate_emails = []
    non_friend_usernames = []
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
                    else:
                        # Check if the tournament creator is friends with this user
                        friendship = Friend.query.filter(
                            (
                                (Friend.user_id == current_user.id) & (Friend.friend_id == existing_user.id)
                            ) | (
                                (Friend.user_id == existing_user.id) & (Friend.friend_id == current_user.id)
                            ),
                            Friend.status == 'accepted'
                        ).first()
                        
                        if not friendship and player_data['username'] != current_user.username:
                            non_friend_usernames.append(player_data['username'])
        
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
    
    if non_friend_usernames:
        error_messages = []
        for username in non_friend_usernames:
            if username != current_user.username:
                error_messages.append(f"You must be friends with '{username}' to add them to your tournament")
            
        return {
            'valid': False,
            'response': {
                'success': False,
                'message': "Non-friend username(s) detected in tournament",
                'non_friend_usernames': non_friend_usernames,
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
        guest_firstname=player_data.get('guest_firstname', ''),
        guest_lastname=player_data.get('guest_lastname', ''),
        email=player_data.get('email', ''),
        is_confirmed=player_data.get('is_confirmed', False)
    )

    if 'user_id' in player_data and player_data['user_id']:
        new_player.user_id = player_data['user_id']
        if player_data['user_id'] == current_user.id:
            new_player.guest_firstname = current_user.first_name
            new_player.guest_lastname = current_user.last_name
    elif 'username' in player_data and player_data['username']:
        existing_user = db.session.query(User).filter_by(username=player_data['username']).first()
        if existing_user:
            new_player.user_id = existing_user.id
            new_player.guest_firstname = existing_user.first_name
            new_player.guest_lastname = existing_user.last_name
    elif player_data.get('email'):
        existing_user = db.session.query(User).filter_by(email=player_data['email']).first()
        if existing_user:
            new_player.user_id = existing_user.id
            new_player.guest_firstname = existing_user.first_name
            new_player.guest_lastname = existing_user.last_name

    return new_player

def create_match(tournament_id, round_number, player1_id, player2_id=None, is_bye=False, status='not started'):
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
            status='not started'
        )
        db.session.add(round_obj)
        db.session.flush()
    
    # Then create the match
    new_match = Match(
        round_id=round_obj.id,
        player1_id=player1_id,
        player2_id=player2_id,
        status='not started'
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

@application.route('/search_players')
def search_players():
    query = request.args.get('query', '')
    
    if not query or len(query) < 1:
        return jsonify({'players': []})

    search_term = f"%{query}%"
    players = User.query.filter(
        User.username.ilike(search_term)
    ).limit(10).all()
    
    results = []
    for player in players:
        results.append({
            'id': player.id,
            'username': player.username,
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