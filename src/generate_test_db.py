from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
import random
import datetime
# No need for dateutil import as we're using standard datetime
import json

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
GAME_TYPES = ["Chess", "Poker", "Magic: The Gathering", "Settlers of Catan", 
              "Dominion", "Ticket to Ride", "Pandemic", "Uno", "Monopoly", "Go"]

def add_users():
    """Add sample users to the database"""
    users_info = [
        {
            "username": "player1",
            "email": "player1@example.com",
            "first_name": "Alex",
            "last_name": "Johnson",
            "display_name": "AlexJ",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": False,
            "show_best_three": True
        },
        {
            "username": "player2",
            "email": "player2@example.com",
            "first_name": "Sam",
            "last_name": "Smith",
            "display_name": "SamTheGamer",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": False
        },
        {
            "username": "player3",
            "email": "player3@example.com",
            "first_name": "Chris",
            "last_name": "Lee",
            "display_name": "ChrisL",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": True
        },
        {
            "username": "player4",
            "email": "player4@example.com",
            "first_name": "Taylor",
            "last_name": "Brown",
            "display_name": "TayB",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": False
        },
        {
            "username": "player5",
            "email": "player5@example.com",
            "first_name": "Jordan",
            "last_name": "Davis",
            "display_name": "JD",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": True
        },
        {
            "username": "player6",
            "email": "player6@example.com",
            "first_name": "Morgan",
            "last_name": "Wilson",
            "display_name": "MorganW",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": False,
            "show_last_three": True,
            "show_best_three": True
        },
        {
            "username": "player7",
            "email": "player7@example.com",
            "first_name": "Casey",
            "last_name": "Miller",
            "display_name": "CM",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": False,
            "show_last_three": False,
            "show_best_three": True
        },
        {
            "username": "player8",
            "email": "player8@example.com",
            "first_name": "Riley",
            "last_name": "Garcia",
            "display_name": "RileyG",
            "password": "password123",
            "show_win_rate": False,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": False
        },
        {
            "username": "organizer1",
            "email": "organizer1@example.com",
            "first_name": "Jamie",
            "last_name": "Williams",
            "display_name": "EventMaster",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": True,
            "show_best_three": True
        },
        {
            "username": "organizer2",
            "email": "organizer2@example.com",
            "first_name": "Quinn",
            "last_name": "Martinez",
            "display_name": "TourneyQ",
            "password": "password123",
            "show_win_rate": True,
            "show_total_wins_played": True,
            "show_last_three": False,
            "show_best_three": False
        }
    ]

    for user_info in users_info:
        new_user = User(
            username=user_info["username"],
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            display_name=user_info["display_name"],
            show_win_rate=user_info["show_win_rate"],
            show_total_wins_played=user_info["show_total_wins_played"],
            show_last_three=user_info["show_last_three"],
            show_best_three=user_info["show_best_three"],
            avatar_path=f"avatars/{user_info['username']}.png"
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
        (1, 2, "accepted"),
        (1, 3, "accepted"),
        (2, 4, "accepted"),
        (3, 5, "accepted"),
        (4, 6, "accepted"),
        (5, 7, "accepted"),
        (6, 8, "accepted"),
        (7, 9, "accepted"),
        (1, 5, "accepted"),
        (2, 6, "accepted"),
        (3, 7, "accepted"),
        (4, 8, "accepted"),
        
        # Some pending friendships
        (1, 7, "pending"),
        (2, 8, "pending"),
        (3, 9, "pending"),
        (4, 10, "pending"),
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
            "title": "Poker Night",
            "game_type": "Poker",
            "format": "single elimination",
            "created_by": 9,
            "status": "in progress",
            "num_players": 6,
            "round_time_minutes": 60,
            "total_rounds": 2,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() - datetime.timedelta(days=1)
        },
        {
            "title": "Settlers of Catan League",
            "game_type": "Settlers of Catan",
            "format": "round robin",
            "created_by": 10,
            "status": "draft",
            "num_players": 4,
            "round_time_minutes": 90,
            "total_rounds": 3,
            "include_creator_as_player": False,
            "start_time": datetime.datetime.now() + datetime.timedelta(days=7)
        },
        {
            "title": "Board Game Bonanza",
            "game_type": "Ticket to Ride",
            "format": "swiss",
            "created_by": 9,
            "status": "draft",
            "num_players": 12,
            "round_time_minutes": 45,
            "total_rounds": 4,
            "include_creator_as_player": True,
            "start_time": datetime.datetime.now() + datetime.timedelta(days=14)
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
    """Add players to tournaments"""
    users = User.query.all()
    user_ids = [user.id for user in users]
    
    for tournament_id, tournament_info in created_tournaments:
        # Add registered users as players
        available_user_ids = user_ids.copy()
        
        # If creator is included as player, add them first
        if tournament_info["include_creator_as_player"]:
            new_player = TournamentPlayer(
                tournament_id=tournament_id,
                user_id=tournament_info["created_by"],
                is_confirmed=True
            )
            db.session.add(new_player)
            available_user_ids.remove(tournament_info["created_by"])
        
        # Fill remaining slots with users or guests
        players_to_add = tournament_info["num_players"]
        
        # Add some users as confirmed players
        confirmed_count = min(players_to_add - 2, len(available_user_ids) - 1)
        if confirmed_count > 0:
            confirmed_users = random.sample(available_user_ids, confirmed_count)
            for user_id in confirmed_users:
                new_player = TournamentPlayer(
                    tournament_id=tournament_id,
                    user_id=user_id,
                    is_confirmed=True
                )
                db.session.add(new_player)
                available_user_ids.remove(user_id)
            players_to_add -= confirmed_count
        
        # Add some users as unconfirmed players
        if players_to_add > 0 and available_user_ids:
            unconfirmed_count = min(players_to_add - 1, len(available_user_ids))
            unconfirmed_users = random.sample(available_user_ids, unconfirmed_count)
            for user_id in unconfirmed_users:
                new_player = TournamentPlayer(
                    tournament_id=tournament_id,
                    user_id=user_id,
                    is_confirmed=False
                )
                db.session.add(new_player)
            players_to_add -= unconfirmed_count
        
        # Fill remaining slots with guests
        for i in range(players_to_add):
            guest_name = f"Guest {i+1}"
            guest_email = f"guest{i+1}@example.com"
            new_player = TournamentPlayer(
                tournament_id=tournament_id,
                guest_name=guest_name,
                email=guest_email,
                is_confirmed=random.choice([True, False])
            )
            db.session.add(new_player)
    
    print("Added tournament players successfully.")
    db.session.commit()

def add_rounds_and_matches(created_tournaments):
    """Create rounds and matches for tournaments"""
    for tournament_id, tournament_info in created_tournaments:
        if tournament_info["status"] in ["in progress", "completed"]:
            # Get players for this tournament
            players = TournamentPlayer.query.filter_by(tournament_id=tournament_id, is_confirmed=True).all()
            
            # Calculate how many rounds to create based on tournament status
            if tournament_info["status"] == "completed":
                rounds_to_create = tournament_info["total_rounds"]
            else:  # in progress
                rounds_to_create = random.randint(1, tournament_info["total_rounds"] - 1)
            
            for round_num in range(1, rounds_to_create + 1):
                # Create round
                round_status = "completed" if round_num < rounds_to_create or tournament_info["status"] == "completed" else "in progress"
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
                    
                    match_status = "completed" if round_status == "completed" else "in progress"
                    winner_id = None
                    
                    if match_status == "completed":
                        winner_id = random.choice([player1.id, player2.id])
                    
                    new_match = Match(
                        round_id=new_round.id,
                        player1_id=player1.id,
                        player2_id=player2.id,
                        winner_id=winner_id,
                        status=match_status,
                        notes=f"Round {round_num} match between {player1.id} and {player2.id}"
                    )
                    db.session.add(new_match)
                
                # If there's an odd player left, they get a bye
                if available_players:
                    # In a real system, you'd handle byes differently
                    pass
    
    print("Added rounds and matches successfully.")
    db.session.commit()

def add_tournament_results(created_tournaments):
    """Generate tournament results for completed tournaments"""
    for tournament_id, tournament_info in created_tournaments:
        if tournament_info["status"] == "completed":
            # Get confirmed players
            players = TournamentPlayer.query.filter_by(tournament_id=tournament_id, is_confirmed=True).all()
            
            for player in players:
                # Calculate wins and losses
                wins = 0
                losses = 0
                
                # Get all matches where this player participated
                rounds = Round.query.filter_by(tournament_id=tournament_id).all()
                for round_obj in rounds:
                    matches = Match.query.filter(
                        Match.round_id == round_obj.id,
                        ((Match.player1_id == player.id) | (Match.player2_id == player.id)),
                        Match.status == "completed"
                    ).all()
                    
                    for match in matches:
                        if match.winner_id == player.id:
                            wins += 1
                        else:
                            losses += 1
                
                # Calculate opponent win percentage (random for this example)
                opponent_win_percentage = random.uniform(0.2, 0.8)
                opp_opp_win_percentage = random.uniform(0.3, 0.7)
                
                new_result = TournamentResult(
                    tournament_id=tournament_id,
                    player_id=player.id,
                    game_type=tournament_info["game_type"],
                    wins=wins,
                    losses=losses,
                    opponent_win_percentage=opponent_win_percentage,
                    opp_opp_win_percentage=opp_opp_win_percentage
                )
                db.session.add(new_result)
    
    print("Added tournament results successfully.")
    db.session.commit()

def add_user_stats():
    """Generate overall user statistics"""
    users = User.query.all()
    
    for user in users:
        # Get all tournaments where user participated
        player_entries = TournamentPlayer.query.filter_by(user_id=user.id, is_confirmed=True).all()
        
        # Group by game type
        game_type_stats = {}
        for player_entry in player_entries:
            tournament = Tournament.query.get(player_entry.tournament_id)
            
            if tournament and tournament.game_type:
                if tournament.game_type not in game_type_stats:
                    game_type_stats[tournament.game_type] = {
                        'played': 0,
                        'won': 0,
                        'lost': 0
                    }
                
                # Get tournament results
                result = TournamentResult.query.filter_by(
                    tournament_id=tournament.id, 
                    player_id=player_entry.id
                ).first()
                
                if result:
                    game_type_stats[tournament.game_type]['played'] += result.wins + result.losses
                    game_type_stats[tournament.game_type]['won'] += result.wins
                    game_type_stats[tournament.game_type]['lost'] += result.losses
        
        # Also add some random game types that might not be in tournaments
        for game_type in random.sample(GAME_TYPES, 3):
            if game_type not in game_type_stats:
                games_played = random.randint(5, 30)
                games_won = random.randint(1, games_played)
                game_type_stats[game_type] = {
                    'played': games_played,
                    'won': games_won,
                    'lost': games_played - games_won
                }
        
        # Create UserStat entries
        for game_type, stats in game_type_stats.items():
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
    
    print("Added user stats successfully.")
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