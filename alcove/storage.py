"""storage.py - saving and loading the library data.

All data lives in ONE dictionary called `state`:

    state = {
        "books":          {isbn: {...book...}},
        "members":        {member_id: {...member...}},
        "loans":          [ {...loan...}, ... ],
        "next_member_id": 1,
    }

The dictionary is stored as a JSON file between runs.
"""

import json
import os

DATA_FILE = os.path.join("data", "alcove_data.json")


def new_state():
    """A brand-new, empty library."""
    return {"books": {}, "members": {}, "loans": [], "next_member_id": 1}


def save_state(state, path=DATA_FILE):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_state(path=DATA_FILE):
    """Load saved data. If the file is missing or unreadable, start empty."""
    if not os.path.exists(path):
        return new_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        # The file must hold a dictionary with all four expected keys.
        if not isinstance(state, dict) or not all(k in state for k in new_state()):
            raise ValueError("unexpected data layout")
        return state
    except (ValueError, OSError):   # JSONDecodeError is a ValueError
        print("! Saved data could not be read. Starting with an empty library.")
        return new_state()
