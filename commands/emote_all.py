import asyncio
from emotes import EMOTE_DICT

async def execute(handler, user, message):
    parts = message.split()
    
    # 1. Stop Logic
    if len(parts) >= 1 and parts[0].lower() in ["/stop", "0"]:
        if handler.all_loop_task:
            handler.all_loop_task.cancel()
            handler.all_loop_task = None
            await handler.bot.highrise.chat("🛑 All emotes stopped.")
        return

    # 2. Start Logic
    if len(parts) < 2:
        return
    
    emote_name = parts[1].lower()
    emote_id = EMOTE_DICT.get(emote_name) or EMOTE_DICT.get(f"emote-{emote_name}")
    
    if not emote_id:
        await handler.bot.highrise.chat(f"❌ Emote '{emote_name}' not found.")
        return

    # Cancel previous task to prevent conflicts
    if handler.all_loop_task:
        handler.all_loop_task.cancel()
        await asyncio.sleep(0.5)

    await handler.bot.highrise.chat(f"✨ Everyone is now doing: {emote_name}")

    async def emote_loop():
        try:
            while True:
                # Check connection status
                if not handler.bot.highrise.ws or handler.bot.highrise.ws.closed:
                    break
                
                room_users = await handler.bot.highrise.get_room_users()
                for room_user, _ in room_users.content:
                    try:
                        await handler.bot.highrise.send_emote(emote_id, room_user.id)
                    except Exception:
                        continue
                
                # Sleep in small increments to allow for quick cancellation
                for _ in range(60): 
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    handler.all_loop_task = asyncio.create_task(emote_loop())
