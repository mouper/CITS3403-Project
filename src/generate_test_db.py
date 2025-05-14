from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
import random
import datetime

# Import models from the models.py file
from models import db, User, Friend, Tournament, TournamentPlayer, Round, Match, TournamentResult, UserStat

app = Flask(__name__)

project_root = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(project_root, "instance")
if not os.path.exists(instance_path):
    os.makedirs(instance_path, exist_ok=True)

db_path = os.path.join(instance_path, "app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Game types for variety
GAME_TYPES = ["Pokémon TCG", "Chess", "Magic: The Gathering", "Checkers", 
              "YuGiOh", "One Piece Card Game"]

def add_users():
    """Add sample users to the database"""
    users_info = [
        {
            "username": "AlexJ",
            "email": "player1@example.com",
            "first_name": "Alex",
            "last_name": "Johnson",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": False,
            "show_best_three": True,
            "show_admin": False,
            "preferred_game_type": "Chess",
            "preferred_top3_sorting": "winrate"
        },
        {
            "username": "SamTheGamer",
            "email": "player2@example.com",
            "first_name": "Sam",
            "last_name": "Smith",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": False,
            "show_admin": False,
            "preferred_game_type": "Pokémon TCG",
            "preferred_top3_sorting": "wins"
        },
        {
            "username": "ChrisL",
            "email": "player3@example.com",
            "first_name": "Chris",
            "last_name": "Lee",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": True,
            "show_admin": False,
            "preferred_game_type": "Magic: The Gathering",
            "preferred_top3_sorting": "winrate"
        },
        {
            "username": "TayB",
            "email": "player4@example.com",
            "first_name": "Taylor",
            "last_name": "Brown",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": False,
            "show_admin": False,
            "preferred_game_type": "Checkers",
            "preferred_top3_sorting": "wins"
        },
        {
            "username": "JD",
            "email": "player5@example.com",
            "first_name": "Jordan",
            "last_name": "Davis",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": True,
            "show_admin": False,
            "preferred_game_type": "YuGiOh",
            "preferred_top3_sorting": "winrate"
        },
        {
            "username": "MorganW",
            "email": "player6@example.com",
            "first_name": "Morgan",
            "last_name": "Wilson",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": False,
            "show_last_three": True,
            "show_best_three": True,
            "show_admin": False,
            "preferred_game_type": "Chess",
            "preferred_top3_sorting": "wins"
        },
        {
            "username": "CM",
            "email": "player7@example.com",
            "first_name": "Casey",
            "last_name": "Miller",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": True,
            "show_admin": False,
            "preferred_game_type": "Pokémon TCG",
            "preferred_top3_sorting": "winrate"
        },
        {
            "username": "RileyG",
            "email": "player8@example.com",
            "first_name": "Riley",
            "last_name": "Garcia",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": False,
            "show_admin": False,
            "preferred_game_type": "Magic: The Gathering",
            "preferred_top3_sorting": "wins"
        },
        {
            "username": "EventMaster",
            "email": "organizer1@example.com",
            "first_name": "Jamie",
            "last_name": "Williams",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": False,
            "show_admin": True,
            "preferred_game_type": "Checkers",
            "preferred_top3_sorting": "winrate"
        },
        {
            "username": "TourneyQ",
            "email": "organizer2@example.com",
            "first_name": "Quinn",
            "last_name": "Martinez",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": False,
            "show_admin": True,
            "preferred_game_type": "YuGiOh",
            "preferred_top3_sorting": "wins"
        }
    ]

    for user_info in users_info:
        new_user = User(
            username=user_info["username"],
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            show_win_rate=user_info["show_win_rate"],
            show_total_wins_played=user_info["show_total_wins_played"],
            show_last_three=user_info["show_last_three"],
            show_best_three=user_info["show_best_three"],
            show_admin=user_info["show_admin"],
            preferred_game_type=user_info.get("preferred_game_type"),
            preferred_top3_sorting=user_info.get("preferred_top3_sorting", "wins")
        )
        new_user.set_password(user_info["password"])
        db.session.add(new_user)
    
    print("Added users successfully.")
    db.session.commit()

def add_friendships():
    """Create friendship relationships between users"""
    users = User.query.all()
    
    # Create some accepted friendships
    friendships = [
        # Original friendships
        (1, 2, "accepted"),
        (1, 3, "accepted"),
        (2, 4, "accepted"),
        (3, 5, "accepted"),
        (4, 6, "accepted"),
        (5, 7, "accepted"),
        (6, 8, "accepted"),
        (7, 9, "accepted"),
        (2, 6, "accepted"),
        (3, 7, "accepted"),
        (4, 8, "accepted"),
        
        # Additional friendships for tournament organizers (EventMaster and TourneyQ)
        (9, 1, "accepted"),  # EventMaster friends with AlexJ
        (9, 2, "accepted"),  # EventMaster friends with SamTheGamer
        (9, 3, "accepted"),  # EventMaster friends with ChrisL
        (9, 4, "accepted"),  # EventMaster friends with TayB
        (9, 5, "accepted"),  # EventMaster friends with JD
        (10, 1, "accepted"), # TourneyQ friends with AlexJ
        (10, 2, "accepted"), # TourneyQ friends with SamTheGamer
        (10, 3, "accepted"), # TourneyQ friends with ChrisL
        (10, 4, "accepted"), # TourneyQ friends with TayB
        (10, 5, "accepted"), # TourneyQ friends with JD
        (10, 6, "accepted"), # TourneyQ friends with MorganW
        (10, 7, "accepted"), # TourneyQ friends with CM
        (10, 8, "accepted"), # TourneyQ friends with RileyG
        
        # Some pending friendships
        (1, 7, "pending"),
        (2, 8, "pending"),
        (5, 1, "pending"),
        (6, 3, "pending")
    ]
    
    for user_id, friend_id, status in friendships:
        new_friendship = Friend(
            user_id=user_id,
            friend_id=friend_id,
            status=status
        )
        db.session.add(new_friendship)
    
    print("Added friendships successfully.")
    db.session.commit()

def add_tournaments():
    """Create tournaments with different formats and statuses"""
    organizer_ids = [9, 10]  # IDs for the organizer users
    
    tournament_data = [
        # Historical Completed Tournaments (4-6 months ago)
        {
            "title": "Winter Chess Classic",
            "game_type": "Chess",
            "format": "swiss",
            "created_by": 9,
            "status": "completed",
            "num_players": 24,
            "round_time_minutes": 45,
            "total_rounds": 5,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=180)
        },
        {
            "title": "New Year Magic Tournament",
            "game_type": "Magic: The Gathering",
            "format": "single elimination",
            "created_by": 10,
            "status": "completed",
            "num_players": 16,
            "round_time_minutes": 50,
            "total_rounds": 4,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=170)
        },
        {
            "title": "Winter Pokémon League",
            "game_type": "Pokémon TCG",
            "format": "swiss",
            "created_by": 9,
            "status": "completed",
            "num_players": 32,
            "round_time_minutes": 45,
            "total_rounds": 6,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=160)
        },
        {
            "title": "YuGiOh Winter Championship",
            "game_type": "YuGiOh",
            "format": "single elimination",
            "created_by": 10,
            "status": "completed",
            "num_players": 16,
            "round_time_minutes": 40,
            "total_rounds": 4,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=150)
        },

        # Historical Completed Tournaments (2-3 months ago)
        {
            "title": "Spring Chess Championship",
            "game_type": "Chess",
            "format": "swiss",
            "created_by": 9,
            "status": "completed",
            "num_players": 16,
            "round_time_minutes": 30,
            "total_rounds": 4,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=90)
        },
        {
            "title": "Magic Masters Series",
            "game_type": "Magic: The Gathering",
            "format": "single elimination",
            "created_by": 10,
            "status": "completed",
            "num_players": 32,
            "round_time_minutes": 50,
            "total_rounds": 5,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=85)
        },
        {
            "title": "Pokémon Regional Championship",
            "game_type": "Pokémon TCG",
            "format": "swiss",
            "created_by": 9,
            "status": "completed",
            "num_players": 24,
            "round_time_minutes": 45,
            "total_rounds": 5,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=75)
        },
        {
            "title": "One Piece Spring Tournament",
            "game_type": "One Piece Card Game",
            "format": "round robin",
            "created_by": 10,
            "status": "completed",
            "num_players": 8,
            "round_time_minutes": 40,
            "total_rounds": 7,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=70)
        },

        # Recently Completed Tournaments (last month)
        {
            "title": "Weekly Chess Tournament",
            "game_type": "Chess",
            "format": "swiss",
            "created_by": 9,
            "status": "completed",
            "num_players": 8,
            "round_time_minutes": 30,
            "total_rounds": 3,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=14)
        },
        {
            "title": "Magic: The Gathering Draft",
            "game_type": "Magic: The Gathering",
            "format": "single elimination",
            "created_by": 10,
            "status": "completed",
            "num_players": 8,
            "round_time_minutes": 50,
            "total_rounds": 3,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=7)
        },
        {
            "title": "One Piece Weekly Series",
            "game_type": "One Piece Card Game",
            "format": "round robin",
            "created_by": 9,
            "status": "completed",
            "num_players": 6,
            "round_time_minutes": 40,
            "total_rounds": 5,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=10)
        },
        {
            "title": "Checkers League Finals",
            "game_type": "Checkers",
            "format": "single elimination",
            "created_by": 10,
            "status": "completed",
            "num_players": 8,
            "round_time_minutes": 30,
            "total_rounds": 3,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=5)
        },

        # Currently In Progress Tournaments
        {
            "title": "Pokémon TCG League",
            "game_type": "Pokémon TCG",
            "format": "single elimination",
            "created_by": 9,
            "status": "in progress",
            "num_players": 16,
            "round_time_minutes": 45,
            "total_rounds": 4,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=1)
        },
        {
            "title": "YuGiOh Championship",
            "game_type": "YuGiOh",
            "format": "swiss",
            "created_by": 10,
            "status": "in progress",
            "num_players": 12,
            "round_time_minutes": 40,
            "total_rounds": 4,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=2)
        },
        {
            "title": "One Piece Card Game Tournament",
            "game_type": "One Piece Card Game",
            "format": "swiss",
            "created_by": 9,
            "status": "in progress",
            "num_players": 12,
            "round_time_minutes": 45,
            "total_rounds": 4,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=1)
        },
        {
            "title": "Chess Rapid Tournament",
            "game_type": "Chess",
            "format": "round robin",
            "created_by": 10,
            "status": "in progress",
            "num_players": 8,
            "round_time_minutes": 15,
            "total_rounds": 7,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(hours=6)
        },

        # Upcoming Tournaments (Draft Status)
        {
            "title": "Pokémon TCG Draft Tournament",
            "game_type": "Pokémon TCG",
            "format": "swiss",
            "created_by": 10,
            "status": "draft",
            "num_players": 8,
            "round_time_minutes": 40,
            "total_rounds": 3,
            "include_creator_as_player": True,
            "start_time": None
        },
        {
            "title": "YuGiOh Weekend Challenge",
            "game_type": "YuGiOh",
            "format": "single elimination",
            "created_by": 9,
            "status": "draft",
            "num_players": 16,
            "round_time_minutes": 45,
            "total_rounds": 4,
            "include_creator_as_player": True,
            "start_time": None
        },
        {
            "title": "Checkers Championship",
            "game_type": "Checkers",
            "format": "round robin",
            "created_by": 10,
            "status": "draft",
            "num_players": 8,
            "round_time_minutes": 30,
            "total_rounds": 7,
            "include_creator_as_player": True,
            "start_time": None
        }
    ]
    
    created_tournaments = []
    
    for tournament_info in tournament_data:
        new_tournament = Tournament(
            title=tournament_info["title"],
            game_type=tournament_info["game_type"],
            format=tournament_info["format"],
            created_by=tournament_info["created_by"],
            status=tournament_info["status"],
            num_players=tournament_info["num_players"],
            round_time_minutes=tournament_info["round_time_minutes"],
            total_rounds=tournament_info["total_rounds"],
            include_creator_as_player=tournament_info["include_creator_as_player"],
            start_time=tournament_info["start_time"]
        )
        db.session.add(new_tournament)
        db.session.flush()  # Flush to get the ID
        created_tournaments.append((new_tournament.id, tournament_info))
    
    print("Added tournaments successfully.")
    db.session.commit()
    
    return created_tournaments

def add_tournament_players(created_tournaments):
    """Add players to tournaments, ensuring creators can only add users they are friends with"""
    users = User.query.all()
    
    for tournament_id, tournament_info in created_tournaments:
        creator_id = tournament_info["created_by"]
        
        # Get all friends of the creator (both sent and received accepted friendships)
        creator_friends = Friend.query.filter(
            ((Friend.user_id == creator_id) | (Friend.friend_id == creator_id)) &
            (Friend.status == "accepted")
        ).all()
        
        # Get friend IDs (excluding the creator)
        friend_ids = set()
        for friendship in creator_friends:
            if friendship.user_id == creator_id:
                friend_ids.add(friendship.friend_id)
            else:
                friend_ids.add(friendship.user_id)
        
        # Convert to list of User objects
        available_friends = [user for user in users if user.id in friend_ids]
        
        # If creator is included as player, add them first
        if tournament_info["include_creator_as_player"]:
            creator = User.query.get(creator_id)
            new_player = TournamentPlayer(
                tournament_id=tournament_id,
                user_id=creator_id,
                is_confirmed=True
            )
            db.session.add(new_player)
        
        # Calculate how many more players we need
        players_to_add = tournament_info["num_players"]
        if tournament_info["include_creator_as_player"]:
            players_to_add -= 1
        
        # Add some friends as confirmed players
        confirmed_count = min(players_to_add - 1, len(available_friends))
        if confirmed_count > 0:
            confirmed_friends = random.sample(available_friends, confirmed_count)
            for friend in confirmed_friends:
                new_player = TournamentPlayer(
                    tournament_id=tournament_id,
                    user_id=friend.id,
                    is_confirmed=True
                )
                db.session.add(new_player)
            players_to_add -= confirmed_count
        
        # Add some friends as unconfirmed players if we still need more
        if players_to_add > 0 and available_friends:
            remaining_friends = [f for f in available_friends if f.id not in [cf.id for cf in confirmed_friends]]
            unconfirmed_count = min(players_to_add - 1, len(remaining_friends))
            if unconfirmed_count > 0:
                unconfirmed_friends = random.sample(remaining_friends, unconfirmed_count)
                for friend in unconfirmed_friends:
                    new_player = TournamentPlayer(
                        tournament_id=tournament_id,
                        user_id=friend.id,
                        is_confirmed=False
                    )
                    db.session.add(new_player)
                players_to_add -= unconfirmed_count
        
        # Fill remaining slots with guests
        for i in range(players_to_add):
            # Generate a complete name for guests
            guest_firstname = random.choice(["Jamie", "Pat", "Robin", "Jordan", "Casey", "Taylor", "Alex", "Morgan"])
            guest_lastname = random.choice(["Smith", "Johnson", "Lee", "Garcia", "Wilson", "Brown", "Taylor", "Martinez"])
            guest_email = f"guest{i+1}@example.com"
            new_player = TournamentPlayer(
                tournament_id=tournament_id,
                guest_firstname=guest_firstname,
                guest_lastname=guest_lastname,
                email=guest_email,
                is_confirmed=random.choice([True, False])
            )
            db.session.add(new_player)
    
    print("Added tournament players successfully.")
    db.session.commit()

def add_rounds_and_matches(created_tournaments):
    """Create rounds and matches for tournaments with proper round status logic"""
    for tournament_id, tournament_info in created_tournaments:
        if tournament_info["status"] in ["in progress", "completed"]:
            # Get players for this tournament
            players = TournamentPlayer.query.filter_by(tournament_id=tournament_id, is_confirmed=True).all()
            
            # Calculate how many rounds to create and their statuses based on tournament status
            total_rounds = tournament_info["total_rounds"]
            
            # For completed tournaments, all rounds are completed
            if tournament_info["status"] == "completed":
                round_statuses = ["completed"] * total_rounds
            else:  # For in-progress tournaments
                # Select a tournament to have a "not started" round
                if tournament_info["title"] in ["Pokémon TCG League", "One Piece Card Game Tournament"] and random.random() < 0.5:
                    # This is one of our chosen tournaments that will have "not started" rounds
                    
                    # Decide how many rounds are complete or in progress
                    active_rounds = random.randint(1, total_rounds - 1)
                    
                    # All rounds before "active_rounds" are completed
                    round_statuses = ["completed"] * (active_rounds - 1)
                    
                    # The active_rounds position is "in progress"
                    round_statuses.append("in progress")
                    
                    # All remaining rounds are "not started"
                    round_statuses.extend(["not started"] * (total_rounds - active_rounds))
                else:
                    # Regular in-progress tournament with no "not started" rounds
                    active_rounds = random.randint(1, total_rounds - 1)
                    round_statuses = ["completed"] * active_rounds
                    round_statuses.append("in progress")
                    round_statuses.extend(["not started"] * (total_rounds - active_rounds - 1))
            
            # Create rounds and matches for this tournament
            for round_num, round_status in enumerate(round_statuses, start=1):
                # Create round
                new_round = Round(
                    tournament_id=tournament_id,
                    round_number=round_num,
                    status=round_status
                )
                db.session.add(new_round)
                db.session.flush()  # Get the round ID
                
                # Create matches - pair players
                available_players = players.copy()
                random.shuffle(available_players)
                
                while len(available_players) >= 2:
                    player1 = available_players.pop()
                    player2 = available_players.pop()
                    
                    # Determine match status based on round status
                    if round_status == "completed":
                        match_status = "completed"
                        winner_id = random.choice([player1.id, player2.id])
                    elif round_status == "in progress":
                        # Some matches in an in-progress round may be completed
                        match_status = random.choice(["in progress", "completed"] + ["in progress"] * 3)
                        winner_id = player1.id if match_status == "completed" and random.random() > 0.5 else None
                    else:  # not started
                        match_status = "not started"
                        winner_id = None
                    
                    new_match = Match(
                        round_id=new_round.id,
                        player1_id=player1.id,
                        player2_id=player2.id,
                        winner_id=winner_id,
                        status=match_status,
                        notes=f"Round {round_num} match between {player1.id} and {player2.id}",
                        is_bye=False
                    )
                    db.session.add(new_match)
                
                # If there's an odd player left, they get a bye
                if available_players:
                    bye_player = available_players.pop()
                    
                    bye_match = Match(
                        round_id=new_round.id,
                        player1_id=bye_player.id,
                        player2_id=None,
                        winner_id=bye_player.id if round_status != "not started" else None,
                        status="completed" if round_status != "not started" else "not started",
                        notes=f"Round {round_num} bye for player {bye_player.id}",
                        is_bye=True
                    )
                    db.session.add(bye_match)
    
    print("Added rounds and matches successfully.")
    db.session.commit()

def add_tournament_results(created_tournaments):
    """Generate tournament results for completed tournaments with accurate ranking"""
    for tournament_id, tournament_info in created_tournaments:
        if tournament_info["status"] == "completed":
            tournament = db.session.get(Tournament, tournament_id)
            players = TournamentPlayer.query.filter_by(tournament_id=tournament_id, is_confirmed=True).all()
            player_ids = [p.id for p in players]

            # Gather all completed matches
            rounds = Round.query.filter_by(tournament_id=tournament_id).all()
            round_ids = [r.id for r in rounds]
            matches = Match.query.filter(Match.round_id.in_(round_ids), Match.status == "completed").all()

            # Build stats for each player
            stats = {pid: {"wins": 0, "losses": 0, "opponents": [], "head_to_head": {}} for pid in player_ids}
            for match in matches:
                p1, p2, winner = match.player1_id, match.player2_id, match.winner_id
                # Byes: only p1 gets a win
                if match.is_bye:
                    if p1:
                        stats[p1]["wins"] += 1
                    continue
                # Track opponents
                if p1 and p2:
                    stats[p1]["opponents"].append(p2)
                    stats[p2]["opponents"].append(p1)
                # Track wins/losses
                if winner == p1:
                    stats[p1]["wins"] += 1
                    if p2:
                        stats[p2]["losses"] += 1
                        stats[p1]["head_to_head"][p2] = stats[p1]["head_to_head"].get(p2, 0) + 1
                elif winner == p2:
                    stats[p2]["wins"] += 1
                    stats[p1]["losses"] += 1
                    stats[p2]["head_to_head"][p1] = stats[p2]["head_to_head"].get(p1, 0) + 1

            # Calculate OWP and OOWP for Swiss
            owp = {}
            oowp = {}
            if tournament.format == "swiss":
                for pid in player_ids:
                    opps = stats[pid]["opponents"]
                    opp_wp = []
                    for opp in opps:
                        if opp in stats:
                            opp_wins = stats[opp]["wins"]
                            opp_losses = stats[opp]["losses"]
                            total = opp_wins + opp_losses
                            if total > 0:
                                opp_wp.append(opp_wins / total)
                    owp[pid] = sum(opp_wp) / len(opp_wp) if opp_wp else 0.0
                for pid in player_ids:
                    opps = stats[pid]["opponents"]
                    opp_owp = [owp[opp] for opp in opps if opp in owp]
                    oowp[pid] = sum(opp_owp) / len(opp_owp) if opp_owp else 0.0

            # Prepare ranking list
            ranking = []
            for pid in player_ids:
                entry = {
                    "player_id": pid,
                    "wins": stats[pid]["wins"],
                    "losses": stats[pid]["losses"],
                    "owp": owp[pid] if tournament.format == "swiss" else 0.0,
                    "oowp": oowp[pid] if tournament.format == "swiss" else 0.0,
                    "head_to_head": stats[pid]["head_to_head"]
                }
                ranking.append(entry)

            # Sort ranking
            if tournament.format == "swiss":
                ranking.sort(key=lambda x: (-x["wins"], -x["owp"], -x["oowp"]))
            elif tournament.format == "round robin":
                # First by wins, then head-to-head if only two tied, else OWP/OOWP
                def rr_sort_key(x):
                    return (-x["wins"],)
                ranking.sort(key=rr_sort_key)
                # Now resolve ties by head-to-head if only two tied
                i = 0
                while i < len(ranking) - 1:
                    j = i
                    # Find group of tied players
                    while j + 1 < len(ranking) and ranking[j]["wins"] == ranking[j+1]["wins"]:
                        j += 1
                    if j > i:
                        tied = ranking[i:j+1]
                        if len(tied) == 2:
                            a, b = tied[0], tied[1]
                            # If a beat b, a stays ahead; if b beat a, swap
                            if a["head_to_head"].get(b["player_id"], 0) > b["head_to_head"].get(a["player_id"], 0):
                                pass  # a stays ahead
                            elif b["head_to_head"].get(a["player_id"], 0) > a["head_to_head"].get(b["player_id"], 0):
                                ranking[i], ranking[i+1] = b, a
                        # If more than two tied, use OWP/OOWP as fallback
                        else:
                            # Calculate OWP/OOWP for these players
                            for entry in tied:
                                opps = stats[entry["player_id"]]["opponents"]
                                opp_wp = []
                                for opp in opps:
                                    if opp in stats:
                                        opp_wins = stats[opp]["wins"]
                                        opp_losses = stats[opp]["losses"]
                                        total = opp_wins + opp_losses
                                        if total > 0:
                                            opp_wp.append(opp_wins / total)
                                entry["owp"] = sum(opp_wp) / len(opp_wp) if opp_wp else 0.0
                            tied.sort(key=lambda x: -x["owp"])
                            ranking[i:j+1] = tied
                    i = j + 1
            else:
                ranking.sort(key=lambda x: -x["wins"])

            # Assign ranks and create TournamentResult
            for idx, entry in enumerate(ranking, 1):
                pid = entry["player_id"]
                new_result = TournamentResult(
                    tournament_id=tournament_id,
                    player_id=pid,
                    game_type=tournament_info["game_type"],
                    rank=idx,
                    wins=entry["wins"],
                    losses=entry["losses"],
                    opponent_win_percentage=entry["owp"],
                    opp_opp_win_percentage=entry["oowp"]
                )
                db.session.add(new_result)
    print("Added tournament results successfully.")
    db.session.commit()

def add_user_stats():
    """Generate overall user statistics based on completed tournament matches only"""
    users = User.query.all()
    
    for user in users:
        # Get all tournaments where user participated
        player_entries = TournamentPlayer.query.filter_by(user_id=user.id, is_confirmed=True).all()
        
        # Group by game type
        game_type_stats = {}
        
        for player_entry in player_entries:
            tournament = db.session.get(Tournament, player_entry.tournament_id)
            
            # Only process completed tournaments
            if tournament and tournament.game_type and tournament.status == "completed":
                if tournament.game_type not in game_type_stats:
                    game_type_stats[tournament.game_type] = {
                        'played': 0,
                        'won': 0,
                        'lost': 0
                    }
                
                # Get all matches for this player in this completed tournament
                rounds = Round.query.filter_by(tournament_id=tournament.id).all()
                for round_obj in rounds:
                    matches = Match.query.filter(
                        Match.round_id == round_obj.id,
                        Match.status == "completed",
                        ((Match.player1_id == player_entry.id) | (Match.player2_id == player_entry.id)),
                        Match.is_bye == False  # Exclude bye matches
                    ).all()
                    
                    for match in matches:
                        game_type_stats[tournament.game_type]['played'] += 1
                        if match.winner_id == player_entry.id:
                            game_type_stats[tournament.game_type]['won'] += 1
                        else:
                            game_type_stats[tournament.game_type]['lost'] += 1
        
        # Create UserStat entries only for game types where the user has played
        for game_type, stats in game_type_stats.items():
            if stats['played'] > 0:  # Only create stats if games were actually played
                win_percentage = stats['won'] / stats['played'] if stats['played'] > 0 else 0
                
                new_stat = UserStat(
                    user_id=user.id,
                    game_type=game_type,
                    games_played=stats['played'],
                    games_won=stats['won'],
                    games_lost=stats['lost'],
                    win_percentage=win_percentage
                )
                db.session.add(new_stat)
    
    print("Added user stats successfully based on completed tournament matches only.")
    db.session.commit()

def init_db():
    """Initialize the database tables if they don't exist"""
    try:
        # Only create tables that don't exist yet
        db.create_all()
        print("Database tables created if they didn't exist.")
    except Exception as e:
        print(f"Error during database initialization: {e}")

def populate_data():
    """Populate the database with test data"""
    add_users()
    add_friendships()
    created_tournaments = add_tournaments()
    add_tournament_players(created_tournaments)
    add_rounds_and_matches(created_tournaments)
    add_tournament_results(created_tournaments)
    add_user_stats()
    print("All test data successfully added to the database!")

if __name__ == "__main__":
    with app.app_context():
        # Check if the database file exists
        if os.path.exists(db_path):
            print(f"Found existing database at {db_path}")
        else:
            print(f"Creating new database at {db_path}")
        
        init_db()
        
        # Check if we already have data
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"Found {existing_users} existing users in the database.")
            proceed = input("Do you want to add more test data? (y/n): ")
            if proceed.lower() != 'y':
                print("Exiting without adding data.")
                exit()
        
        populate_data()
        print(f"Successfully added test data to the existing app.db in {instance_path}!")