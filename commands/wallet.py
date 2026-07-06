async def execute(handler, user, message):
    try:
        # Highrise provides a way to get the bot's own wallet
        wallet = await handler.bot.highrise.get_wallet()
        
        # Format the wallet response
        # The API usually returns a list of items/balances
        balance_msg = "💰 Bot Wallet: "
        for item in wallet.content:
            balance_msg += f"{item.amount} {item.type}, "
            
        await handler.bot.highrise.chat(balance_msg.rstrip(", "))
        
    except Exception as e:
        print(f"Wallet error: {e}")
        await handler.bot.highrise.chat("❌ Could not retrieve wallet balance. (API Access Restricted)")