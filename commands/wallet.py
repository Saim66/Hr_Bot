# commands/wallet.py

async def execute(handler, user, message):
    try:
        wallet = await handler.bot.highrise.get_wallet()
        total_gold = sum(item.amount for item in wallet.content if hasattr(item, 'amount'))
        await handler.bot.highrise.chat(f"💰 Bot Wallet Balance: {total_gold} Gold")
    except Exception as e:
        await handler.bot.highrise.chat(f"❌ Error: {e}")