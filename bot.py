# bot.py
from main import AdvancedBot
import config

# Point the legacy runner directly to your AdvancedBot class
HighriseBot = AdvancedBot
API_KEY = config.API_KEY
ROOM_ID = config.ROOM_ID