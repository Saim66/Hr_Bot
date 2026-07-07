import asyncio
from emotes import EMOTE_DICT
import asyncio

async def execute(handler, user, message):
    parts = message.split()
    if len(parts) < 2:
        await handler.bot.highrise.chat("Usage: /all [emote_name]")
        return
    
    emote_name = parts[1].lower()
    
    # 1. Stop any existing global loop
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        handler.all_loop_task = None
    
    # 2. Start the new loop as a background task
    handler.all_loop_task = asyncio.create_task(run_all_emote(handler, emote_name))
    await handler.bot.highrise.chat(f"📢 Everyone is now doing: {emote_name}")

async def run_all_emote(handler, emote_name):
    try:
        while True:
            room_users = await handler.bot.highrise.get_room_users()
            for user, position in room_users.content:
                try:
                    await handler.bot.highrise.send_emote(emote_name, user.id)
                except:
                    continue
            await asyncio.sleep(6) # Wait before repeating the cycle
    except asyncio.CancelledError:
        pass # Task was cancelled by a new request

        except Exception as e:
            print(f"Loop error: {e}")

    # Start the task and store it in handler.active_tasks
    handler.active_tasks["all_command"] = asyncio.create_task(emote_loop())