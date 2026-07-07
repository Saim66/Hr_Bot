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
        await handler.bot.highrise.chat("Emote not found.")
        return

    # Cancel existing task if running
    await handler.stop_all_emotes("all_command")

    # Send confirmation message to the room
    await handler.bot.highrise.chat(f"✨ Starting '{emote_name}' loop for everyone!")

    async def emote_loop():
        try:
            while True:
                # Check connection before API calls to prevent crashes
                if not handler.bot.highrise.ws or handler.bot.highrise.ws.closed:
                    break
                
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    try:
                        await handler.bot.highrise.send_emote(emote_id, room_user.id)
                    except Exception:
                        continue # Skip users where emote fails
                
                await asyncio.sleep(6)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Loop error: {e}")

    # Start the task and store it in handler.active_tasks
    handler.active_tasks["all_command"] = asyncio.create_task(emote_loop())
