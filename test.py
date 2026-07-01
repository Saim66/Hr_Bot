# test_import.py
try:
    from emotes import ALL_EMOTES
    print("Success: Emotes imported!")
except Exception as e:
    print(f"Failed: {e}")