import threading
import time
import requests
import os
import base64
from flask import Flask, request, jsonify, send_file
from pythonosc import udp_client

app = Flask(__name__)
main_servers = []
MP3_FOLDER = 'webfiles'  # Ensure this folder contains your .mp3 files
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

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

@app.route('/trigger_all', methods=['POST'])
def trigger_all():
    data = request.json
    action = data.get('action')
    payload = data.get('payload', {})

    results = {}
    for ip in main_servers:
        try:
            url = f"http://{ip}/trigger"
            resp = requests.post(url, json={'action': action, **payload}, timeout=5)
            results[ip] = resp.json()
        except Exception as e:
            results[ip] = str(e)
    return jsonify(results)

@app.route('/play_pad', methods=['POST'])
def play_pad():
    data = request.json
    pad = data.get('pad')
    if pad is not None:
        osc_address = f'/2/push{pad}'
        osc_client.send_message(osc_address, [1])
        # Find the mp3 file containing the pad number
        mp3_file = None
        for fname in os.listdir(MP3_FOLDER):
            if fname.endswith('.mp3') and str(pad) in fname:
                mp3_file = os.path.join(MP3_FOLDER, fname)
                break
        if mp3_file and os.path.isfile(mp3_file):
            return send_file(mp3_file, mimetype='audio/mpeg')
        else:
            return jsonify({'error': f'No MP3 found for pad {pad}'}), 404
    return jsonify({'error': 'Pad not specified'}), 400

@app.route('/stop_sounds', methods=['POST'])
def stop_sounds():
    osc_client.send_message('/2/push16', [1])
    return jsonify({'status': 'All sounds stopped'}), 200

@app.route('/set_tank_level', methods=['POST'])
def set_tank_level():
    data = request.json
    tank_id = data.get('tank_id')
    level = data.get('level')
    if tank_id in [1, 2, 3] and level is not None:
        osc_address = f'/1/fader{tank_id}'
        osc_client.send_message(osc_address, [level])
        return jsonify({'status': f'Tank {tank_id} level set to {level}'}), 200
    return jsonify({'error': 'Invalid tank_id or level'}), 400

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'}), 200

def heartbeat_checker():
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

if __name__ == '__main__':
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
