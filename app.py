from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# --- WEB API ENDPOINTS ---
@app.route('/api/bot/command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    # This sends the command directly into your bot's logic
    # We will hook this into the bot object in main.py
    return jsonify({"status": "sent", "cmd": cmd})

@app.route('/api/locations', methods=['GET'])
def get_locations():
    if os.path.exists("locations.json"):
        with open("locations.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify({})

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')