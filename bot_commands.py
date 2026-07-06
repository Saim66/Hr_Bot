import importlib

async def handle_command(handler_instance, user, message):
    msg = message.strip().lower()
    parts = msg.split()
    if not parts: return
    
    trigger = parts[0].lstrip("/") # Remove "/" so "!help" becomes "help"
    
    # Map specific triggers to files
    mapping = {
        "help": "help",
        "welcome": "welcome",
        "vip": "vip",
        "s": "movement", "to": "movement", "cords": "movement",
        "kick": "moderation", "ban": "moderation",
        "set": "locations", "dloc": "locations", "deleteloc": "locations", "clocs": "locations",
        "all": "emote_all",
        "wallet": "wallet",
        "tip": "tip",
        "stop": "loops", "0": "loops"
    }

    # Handle Emote Loops (since they are in EMOTE_DICT)
    from emotes import EMOTE_DICT
    if trigger in EMOTE_DICT or trigger in mapping:
        module_name = mapping.get(trigger, "loops")
        try:
            module = importlib.import_module(f"commands.{module_name}")
            await module.execute(handler_instance, user, message)
        except Exception as e:
            print(f"Error executing {module_name}: {e}")

# Keep your __init__, load_data, save_data, etc.

async def execute(self, user, message: str) -> None:
    from commands import handle_command
    await handle_command(self, user, message)