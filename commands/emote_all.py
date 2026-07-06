import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = parts[1]
    emote_id = EMOTE_DICT.get(emote_name)

    if not emote_id:
        await handler.bot.highrise.chat(f"Emote '{emote_name}' not found.")
        return

    # Fetch users correctly
    room_users = await handler.bot.highrise.get_room_users()
    
    # room_users.content is a list of (User, Position) tuples
    for room_user, position in room_users.content:
        try:
            print(f"DEBUG: Sending {emote_id} to {room_user.username}")
            await handler.bot.highrise.send_emote(emote_id, room_user.id)
            # Short sleep to prevent rate limiting
            await asyncio.sleep(0.5) 
        except Exception as e:
            print(f"Error emoting {room_user.username}: {e}")