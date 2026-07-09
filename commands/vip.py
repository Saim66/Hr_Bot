import json
import os
import config

# Path to your persistent volume
DATA_FILE = "/var/lib/containers/railwayapp/bind-mounts/vol_iatnm6uo2p12iuk5/bot_data.json"

async def execute(handler, user, message):
    # Permission Check: Only Owner can modify the VIP list
    if not config.is_owner(user.username):
        await handler.bot.highrise.chat(f"🚫 @{user.username}, only the Owner can manage VIPs.")
        return

    parts = message.split()
    
    # 1. LIST VIPs COMMAND (/vips)
    if len(parts) == 1 or parts[1].lower() == "list":
        vips = handler.data.get("vips", [])
        if not vips:
            await handler.bot.highrise.chat("📜 The VIP list is currently empty.")
        else:
            vip_list = ", ".join(vips)
            await handler.bot.highrise.chat(f"📜 Current VIPs: {vip_list}")
        return

    # 2. ADD/REMOVE COMMANDS (/vip [add/remove] @username)
    if len(parts) < 3:
        await handler.bot.highrise.chat("Usage: /vip [add/remove] [@username] or /vip list")
        return

    action = parts[1].lower()
    target_name = parts[2].lstrip("@").lower()

    if action == "add":
        if target_name not in handler.data.get("vips", []):
            handler.data.setdefault("vips", []).append(target_name)
            handler.save_data() 
            await handler.bot.highrise.chat(f"✅ @{target_name} added to VIP list.")
        else:
            await handler.bot.highrise.chat(f"@{target_name} is already a VIP.")

    elif action == "remove":
        if target_name in handler.data.get("vips", []):
            handler.data["vips"].remove(target_name)
            handler.save_data()
            await handler.bot.highrise.chat(f"✅ @{target_name} removed from VIP list.")
        else:
            await handler.bot.highrise.chat(f"@{target_name} is not in the VIP list.")
