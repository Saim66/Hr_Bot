# commands/loops.py
import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    msg = message.strip().lower()
    trigger = msg.split()[0]

    if trigger in EMOTE_DICT:
        actual_emote = EMOTE_DICT[trigger]
        args = msg.split()[1:]
        target_name = args[0].replace("@", "").lower() if args else user.username.lower()
        
        room_users = (await handler.bot.highrise.get_room_users()).content
        target = next((r for r, _ in room_users if r.username.lower() == target_name), None)
        
        if target:
            if target_name in handler.active_tasks:
                handler.looping_users[target_name] = False
                handler.active_tasks[target_name].cancel()
                await asyncio.sleep(0.5)
            
            handler.looping_users[target_name] = True
            task = asyncio.create_task(handler.loop_emote(actual_emote, target.id, target_name))
            handler.active_tasks[target_name] = task
            await handler.bot.highrise.chat(f"✨ Looping {trigger} for @{target_name}!")
            
    elif trigger in ["stop", "0"]:
        name_to_stop = user.username.lower()
        if name_to_stop in handler.active_tasks:
            handler.looping_users[name_to_stop] = False
            handler.active_tasks[name_to_stop].cancel()
            await handler.bot.highrise.chat(f"⏹️ Stopped your emote loop.")