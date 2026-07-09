import os

# --- 1. SENSITIVE CREDENTIALS ---
TOKEN = os.getenv("HR_TOKEN")
ROOM_ID = os.getenv("HR_ROOM_ID")

# --- 2. PERSISTENT STORAGE PATH ---
# This matches your Railway Volume path. 
# Make sure this folder exists on your volume!
VOLUME_PATH = "/var/lib/containers/railwayapp/bind-mounts/vol_iatnm6uo2p12iuk5"
DATA_FILE = os.path.join(VOLUME_PATH, "bot_data.json")

# --- 3. ROLE MANAGEMENT ---
OWNERS = [os.getenv("OWNER_USERNAME", "saim06").lower()]

def is_owner(username):
    return username.lower() in OWNERS

# --- 4. AUTHORIZATION HELPER ---
# Now reads directly from the file on the volume
import json

def is_authorized(username):
    """Checks if a user is an Owner, or listed as a VIP in the JSON file."""
    if is_owner(username):
        return True
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return username.lower() in [u.lower() for u in data.get("vips", [])]
        except:
            return False
    return False
