from __future__ import annotations

AURA_REWARDS: dict[str, int] = {
    "easy": 10,
    "medium": 25,
    "hard": 50,
}

BRAIN_ROT_AURA_REWARD = 30

TIMER_SECONDS = 10

# Maps OpenTDB category IDs to (name, slug, icon) tuples.
OPENTDB_CATEGORIES: dict[int, tuple[str, str, str]] = {
    9: ("General Knowledge", "general-knowledge", "brain"),
    17: ("Science & Nature", "science-nature", "flask-conical"),
    18: ("Computers", "computers", "monitor"),
    22: ("Geography", "geography", "globe"),
    23: ("History", "history", "landmark"),
    25: ("Art", "art", "palette"),
    27: ("Animals", "animals", "paw-print"),
    31: ("Anime & Manga", "anime-manga", "swords"),
    15: ("Video Games", "video-games", "gamepad-2"),
    11: ("Film", "film", "clapperboard"),
    12: ("Music", "music", "music"),
    14: ("Television", "television", "tv"),
    20: ("Mythology", "mythology", "scroll"),
    21: ("Sports", "sports", "trophy"),
}

BRAIN_ROT_CATEGORIES: list[tuple[str, str, str]] = [
    ("Slang & Vibes", "slang-vibes", "message-circle"),
    ("Meme History", "meme-history", "image"),
    ("Creator Lore", "creator-lore", "video"),
    ("Internet Moments", "internet-moments", "wifi"),
]
