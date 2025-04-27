# main_server.py
import os
import base64
import requests
import threading
import time
from flask import Flask, request, jsonify
from pythonosc import udp_client

app = Flask(__name__)
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

MP3_FOLDER = 'webfiles'

API_SERVER_URL = os.getenv('API_SERVER_URL', 'https://api.nanditakumar.com')  # Set this env variable!

def get_global_ip():
    try:
        ip_services = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip",
            "https://icanhazip.com"
        ]
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        print("Warning: Could not determine global IP, fallback to localhost")
        return "127.0.0.1"
    except Exception as e:
        print(f"Error getting global IP: {e}")
        return "127.0.0.1"

def register_with_api_server():
    global_ip = get_global_ip()
    port = 5000
    full_address = f"{global_ip}:{port}"

    print(f"Registering with global IP: {full_address}")

    while True:
        try:
            response = requests.post(f"{API_SERVER_URL}/register", json={"ip": full_address})
            if response.status_code == 200:
                print(f"Successfully registered with API server: {full_address}")
            else:
                print(f"Failed to register: {response.text}")
        except Exception as e:
            print(f"Registration error: {e}")
        
        time.sleep(15)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'alive'}), 200

@app.route('/trigger', methods=['POST'])
def trigger():
    data = request.json
    action = data.get('action')

    if action == 'play_pad':
        pad = data.get('pad')
        if pad is not None:
            osc_address = f'/2/push{pad}'
            osc_client.send_message(osc_address, [1])
            mp3_file = None
            for fname in os.listdir(MP3_FOLDER):
                if fname.endswith('.mp3') and str(pad) in fname:
                    mp3_file = os.path.join(MP3_FOLDER, fname)
                    break
            if mp3_file and os.path.isfile(mp3_file):
                with open(mp3_file, 'rb') as f:
                    mp3_bytes = f.read()
                mp3_b64 = base64.b64encode(mp3_bytes).decode('utf-8')
                return jsonify({'filename': os.path.basename(mp3_file), 'data': mp3_b64})
            else:
                return jsonify({'error': f'No MP3 found for pad {pad}'}), 404

    elif action == 'stop_sounds':
        osc_client.send_message('/2/push16', [1])
        return jsonify({'status': 'sounds stopped'})

    elif action == 'set_tank_level':
        tank_id = data.get('tank_id')
        level = data.get('level')
        if tank_id in [1,2,3] and level is not None:
            osc_address = f'/1/fader{tank_id}'
            osc_client.send_message(osc_address, [level])
            return jsonify({'status': f'tank {tank_id} set to level {level}'})

    return jsonify({'error': 'Invalid action'}), 400

if __name__ == '__main__':
    threading.Thread(target=register_with_api_server, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
