from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import sys
import os

app = Flask(__name__)

# Tracks our background bot process
bot_process = None

# Simple HTML dashboard interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Highrise Bot Control Panel</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1e1e2e; color: #cdd6f4; max-width: 800px; margin: 40px auto; padding: 20px; }
        .card { background: #313244; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1, h2 { color: #89b4fa; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-start { background: #a6e3a1; color: #11111b; }
        .btn-stop { background: #f38ba8; color: #11111b; }
        .btn-add { background: #89b4fa; color: #11111b; }
        .status-on { color: #a6e3a1; font-weight: bold; }
        .status-off { color: #f38ba8; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; margin: 10px 0; background: #45475a; border: 1px solid #585b70; color: #cdd6f4; border-radius: 4px; box-sizing: border-box; }
        label { font-weight: bold; color: #b4befe; }
    </style>
</head>
<body>
    <h1>🤖 Highrise Bot Live Dashboard</h1>
    
    <div class="card">
        <h2>Engine Status: 
            {% if bot_running %}
                <span class="status-on">ONLINE</span>
            {% else %}
                <span class="status-off">OFFLINE</span>
            {% endif %}
        </h2>
        {% if not bot_running %}
            <a href="/start" class="btn btn-start">🚀 Boot Bot</a>
        {% else %}
            <a href="/stop" class="btn btn-stop">🛑 Shut Down Bot</a>
        {% endif %}
    </div>

    <div class="card">
        <h2>➕ Add Automated Custom Command</h2>
        <form action="/add_command" method="POST">
            <label>Command Name (e.g., hello)</label>
            <input type="text" name="command_name" placeholder="Do not include the !" required>
            
            <label>Bot Response Text</label>
            <textarea name="response_text" rows="3" placeholder="What should the bot say in public chat?" required></textarea>
            
            <button type="submit" class="btn btn-add">🔨 Inject Command into main.py</button>
        </form>
    </div>
</body>
</html>
"""

def get_bot_paths():
    """Helper function to cleanly discover consistent paths across all routes."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    start_script = os.path.join(project_root, "start.py")
    
    if not os.path.exists(venv_python):
        venv_python = sys.executable
        
    return project_root, venv_python, start_script

@app.route('/')
def home():
    global bot_process
    bot_running = bot_process is not None and bot_process.poll() is None
    return render_template_string(HTML_TEMPLATE, bot_running=bot_running)

@app.route('/start')
def start_bot():
    global bot_process
    if bot_process is None or bot_process.poll() is not None:
        project_root, venv_python, start_script = get_bot_paths()

        print(f"🔄 Spawning runner executable via path: {venv_python}")
        print(f"📜 TARGET SCRIPT: {start_script}")

        bot_process = subprocess.Popen(
            [venv_python, start_script],
            cwd=project_root
        )
    return redirect(url_for('home'))

@app.route('/stop')
def stop_bot():
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process.wait()
        bot_process = None
    return redirect(url_for('home'))

@app.route('/add_command', methods=['POST']) 
def add_command():
    cmd_name = request.form.get('command_name', '').strip().lower()
    resp_text = request.form.get('response_text', '').strip() # Fixed missing assignment crash

    if not cmd_name or not resp_text:
        return redirect(url_for('home'))

    project_root, venv_python, start_script = get_bot_paths()
    main_py_path = os.path.join(project_root, "main.py")

    # Read current main.py file content safely
    if os.path.exists(main_py_path):
        with open(main_py_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Dynamic target search
        target_idx = None
        for idx, line in enumerate(lines):
            if 'if command == "menu":' in line or "if command == 'menu':" in line:
                target_idx = idx
                break

        if target_idx is not None:
            new_command_block = [
                f"        if command == \"{cmd_name}\":\n",
                f"            await self.highrise.chat(\"{resp_text}\")\n",
                "            return\n\n"
            ]
            lines = lines[:target_idx] + new_command_block + lines[target_idx:]

            with open(main_py_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
                
    # Auto-restart engine with identical safe absolute configurations
    global bot_process
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process.wait()
        
    bot_process = subprocess.Popen(
        [venv_python, start_script],
        cwd=project_root
    )

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
