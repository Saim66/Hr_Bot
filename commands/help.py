async def execute(handler, user, message):
    # Set your owner username here
    OWNER_NAME = "saim06" 
    
    # 1. OWNER VIEW (Shows everything)
    if user.username.lower() == OWNER_NAME.lower():
        help_text = (
            "👑 **Owner Commands**\n"
            "• All commands: /setwelcome, /s, /to, /cords, /kick, /ban, /unban, /set, /dloc, /clocs, /wallet, /tip, /stop, /all\n"
            "• You have full access."
        )
    # 2. NORMAL USER VIEW (Limited commands)
    else:
        help_text = (
            "📜 **Commands**\n"
            "• Emotes: Type emote name (e.g., 'dance'), /stop, /0\n"
            "• Welcome: /setwelcome [message]\n"
            "• Movement: /s [user]\n"
            "/setwelcome, /s, /to"
            
        )
    
    await handler.bot.highrise.send_whisper(user.id, help_text)
