import os

# --- 1. SENSITIVE CREDENTIALS (Loaded from Railway Env Variables) ---
# Never hardcode these in production! 
# Set these in your Railway Dashboard -> Variables tab.
TOKEN = os.getenv("HR_TOKEN")
ROOM_ID = os.getenv("HR_ROOM_ID")

# --- 2. FALLBACK/DEFAULT SETTINGS ---
# Only use these if Environment Variables are not found
API_TOKEN = os.getenv("HR_TOKEN", "04283e4c562763702122cebce3ccf27689e0d61cd2b44b2acd03d548c7b90cbb")
BOT_NAME = "MyHighriseBot"
PREFIX = "/"

# --- 3. ROLE MANAGEMENT ---
# Using a list allows you to add more owners later without changing code logic
OWNERS = [os.getenv("OWNER_USERNAME", "saim06").lower()]

# --- 4. MODERATION & WORLD SETTINGS ---
BANNED_WORDS = ["badword1", "badword2", "toxicword"]
# Persist these in a database or JSON file, not here, as this list clears on restart
DYNAMIC_BANNED_USERS = [] 

# Default Coordinates
SPAWN_POSITION = {"x": 0, "y": 0, "z": 0, "facing": "FrontLeft"}

# --- 5. UTILITY FUNCTION ---
def is_owner(username):
    """Helper to check if a user is in the owner list."""
    return username.lower() in OWNERS
