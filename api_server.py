import os
import base64
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
main_servers = []

MP3_FOLDER = 'webfiles'  # API server's own MP3 folder

# ------------------------- API ROUTES -------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    ip = data.get('ip')
    if ip:
        if ip not in main_servers:
            main_servers.append(ip)
            print(f"Registered new main server: {ip}")
        return jsonify({'message': 'Registered successfully'}), 200
    return jsonify({'error': 'Invalid IP'}), 400

@app.route('/play_pad', methods=['POST'])
def play_pad():
    data = request.json
    pad = data.get('pad')
    if pad is None:
        return jsonify({'error': 'Pad not specified'}), 400

    # 1. Local action: find and send back mp3
    mp3_file = None
    for fname in os.listdir(MP3_FOLDER):
        if fname.endswith('.mp3') and str(pad) in fname:
            mp3_file = os.path.join(MP3_FOLDER, fname)
            break

    if mp3_file and os.path.isfile(mp3_file):
        with open(mp3_file, 'rb') as f:
            mp3_bytes = f.read()
        mp3_b64 = base64.b64encode(mp3_bytes).decode('utf-8')
        mp3_response = {'filename': os.path.basename(mp3_file), 'data': mp3_b64}
    else:
        mp3_response = {'error': f'No MP3 found for pad {pad}'}

    # 2. New action: trigger all main servers
    trigger_main_servers('play_pad', payload={'pad': pad})

    return jsonify(mp3_response)

@app.route('/stop_sounds', methods=['POST'])
def stop_sounds():
    # 1. No local sound action needed here

    # 2. New action: trigger all main servers
    trigger_main_servers('stop_sounds')

    return jsonify({'status': 'All sounds stopped'})

@app.route('/set_tank_level', methods=['POST'])
def set_tank_level():
    data = request.json
    tank_id = data.get('tank_id')
    level = data.get('level')
    if tank_id not in [1, 2, 3] or level is None:
        return jsonify({'error': 'Invalid tank_id or level'}), 400

    # 1. No local tank control needed here

    # 2. New action: trigger all main servers
    trigger_main_servers('set_tank_level', payload={'tank_id': tank_id, 'level': level})

    return jsonify({'status': f'Tank {tank_id} level set to {level}'})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'}), 200

# ------------------------- Helper Functions -------------------------

def trigger_main_servers(action, payload={}):
    """Trigger all registered main servers with a given action"""
    print(f"Triggering all main servers: action={action}, payload={payload}")
    for ip in main_servers.copy():
        try:
            url = f"http://{ip}/trigger"
            data = {'action': action, **payload}
            resp = requests.post(url, json=data, timeout=5)
            if resp.status_code == 200:
                print(f"Triggered {ip} successfully.")
            else:
                print(f"Trigger failed for {ip}: {resp.text}")
        except Exception as e:
            print(f"Error triggering {ip}: {e}")

def heartbeat_checker():
    """Periodically check if main servers are alive"""
    while True:
        time.sleep(30)
        for ip in main_servers.copy():
            try:
                resp = requests.get(f"http://{ip}/ping", timeout=5)
                if resp.status_code == 200:
                    print(f"Main server {ip} alive")
                else:
                    print(f"Main server {ip} not responding correctly")
            except:
                print(f"Removing dead main server: {ip}")
                main_servers.remove(ip)

# ------------------------- Main -------------------------

if __name__ == '__main__':
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
