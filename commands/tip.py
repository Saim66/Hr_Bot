import asyncio
import logging

# Configure logger for tracking transactions
logger = logging.getLogger(__name__)

async def execute(handler, user, message):
    args = message.split()
    if len(args) < 2:
        await handler.bot.highrise.chat("Usage: /tipall [amount]")
        return

    amount = args[1]
    item_id = f"gold_bar_{amount}"
    
    # 1. Strict Validation
    valid_ids = ["gold_bar_1", "gold_bar_5", "gold_bar_10", "gold_bar_50", "gold_bar_100", 
                 "gold_bar_500", "gold_bar_1000", "gold_bar_5000", "gold_bar_10000"]
    
    if item_id not in valid_ids:
        await handler.bot.highrise.chat("❌ Invalid amount. Use 1, 5, 10, 50, 100, 500, 1000, 5000, 10000.")
        return

    # 2. Refresh Room Data (Essential for real-time accuracy)
    try:
        room_users_response = await handler.bot.highrise.get_room_users()
        room_users = room_users_response.content
    except Exception as e:
        logger.error(f"Failed to fetch room users: {e}")
        await handler.bot.highrise.chat("❌ Error: Could not refresh room data.")
        return

    # 3. Target Filtering (Exclude sender and self)
    targets = [u for u, pos in room_users if u.id != user.id and u.id != handler.bot.user_id]
    
    if not targets:
        await handler.bot.highrise.chat("⚠️ No other users found in the room.")
        return

    await handler.bot.highrise.chat(f"⏳ Initiating transfer: {amount} gold to {len(targets)} users...")
    
    # 4. Process Loop with Error Resilience
    count = 0
    for target_user in targets:
        try:
            # We perform the tip request
            await handler.bot.highrise.tip_user(target_user.id, item_id)
            count += 1
            logger.info(f"Successfully tipped {target_user.username} ({target_user.id})")
            
            # Use dynamic sleep based on room size to prevent rate-limit spikes
            await asyncio.sleep(1.2) 
            
        except Exception as e:
            # Log failure but do not break the entire loop
            logger.warning(f"Failed to tip {target_user.username}: {str(e)[:50]}")
            continue
            
    # 5. Final Confirmation
    await handler.bot.highrise.chat(f"✅ Transaction Complete: {amount} gold sent to {count} users.")
