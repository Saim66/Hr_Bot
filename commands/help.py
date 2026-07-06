# commands/help.py
async def execute(handler, user, message):
    await handler.bot.highrise.chat("📜 Commands: /welcome, /s, /to, /kick, /ban")