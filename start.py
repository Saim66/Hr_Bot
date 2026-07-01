import asyncio
import config
from highrise.__main__ import main

if __name__ == "__main__":
    try:
        asyncio.run(main([config.ROOM_ID, config.API_TOKEN]))
    except ExceptionGroup as eg:
        for exc in eg.exceptions:
            print(f"❌ Real Error: {exc}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")