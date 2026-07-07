import asyncio

# Use this in your moderation.py or wherever your kick/ban logic lives
async def moderate_user(bot, target_id, action):
    """
    action: "kick", "ban", or "unban"
    """
    try:
        if action == "kick":
            await bot.highrise.moderate_room(target_id, "kick")
        elif action == "ban":
            # For bans, you can include a duration in seconds (e.g., 3600 for 1 hour)
            await bot.highrise.moderate_room(target_id, "ban", 3600)
        elif action == "unban":
            await bot.highrise.moderate_room(target_id, "unban")
            
        await bot.highrise.chat(f"Successfully performed {action} on user.")
    except Exception as e:
        await bot.highrise.chat(f"Failed to moderate: {e}")
