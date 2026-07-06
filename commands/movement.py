from highrise import Position

async def execute(handler, user, message):
    parts = message.split()
    cmd = parts[0].lstrip("/").lower()
    
    # 1. Sit/Stand (S)
    if cmd == "s":
        # Toggle sitting logic: This usually involves sending the user to a chair or position
        # For simple sit, you can use highrise.sit_user(user.id, "chair_id")
        await handler.bot.highrise.chat(f"@{user.username}, I am ready to move you!")

    # 2. Teleport to Coordinates (TO)
    # Usage: /to 10 0 10 FrontLeft
    elif cmd == "to":
        if len(parts) < 5:
            await handler.bot.highrise.chat("Usage: /to [x] [y] [z] [facing]")
            return
        
        try:
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            facing = parts[4] # e.g., FrontLeft, FrontRight, BackLeft, BackRight
            
            await handler.bot.highrise.teleport(user.id, Position(x, y, z, facing))
            await handler.bot.highrise.chat(f"Teleported @{user.username} to {x}, {y}, {z}")
        except Exception as e:
            await handler.bot.highrise.chat("Invalid coordinates or direction.")
            print(f"Movement error: {e}")

    # 3. Get Coordinates (CORDS)
    elif cmd == "cords":
        room_users = await handler.bot.highrise.get_room_users()
        for u, pos in room_users.content:
            if u.id == user.id:
                await handler.bot.highrise.chat(f"@{user.username}: {pos.x}, {pos.y}, {pos.z} - {pos.facing}")
                return