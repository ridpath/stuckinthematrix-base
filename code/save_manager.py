import json
import os
from support import get_path

def save_game(data, filepath='savegame.json'):
    """
    Saves the provided game state to a JSON file.

    Args:
        data (dict): Game state dictionary to save.
        filepath (str): File path to write to. Defaults to 'savegame.json'.
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[ERROR] Could not save game: {e}")

def load_game(filepath='savegame.json'):
    """
    Loads game state from a JSON file.

    Args:
        filepath (str): Path to the saved file.

    Returns:
        dict: Loaded game state, or None if not found or corrupted.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load save file: {e}")
        return None
