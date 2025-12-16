import csv
import os
from datetime import datetime

def save_game(game_data):
    """Saves the game data to a CSV file."""
    file_path = "data/games.csv"
    file_exists = os.path.isfile(file_path)

    fieldnames = [
        'game_id', 'winner', 'turns', 'start_time', 'end_time',
        'player1_type', 'player2_type', 'history'
    ]

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(game_data)
