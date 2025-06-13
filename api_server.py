import os
import re
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mimetypes
import threading
import random
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://soundingtheinvisible.nanditakumar.com"]}})
MP3_FOLDER = 'webfiles'

# Firebase initialization
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://soundingtheinvisible-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def sanitize_pad(pad):
    # Only allow positive integers, nothing else
    if not str(pad).isdigit():
        return None
    return int(pad)

@app.route('/play_pad', methods=['GET', 'POST'])
def play_pad():
    if request.method == 'POST':
        print("GOT POST REQUEST")
        data = request.json or {}
        pad = data.get('pad')
        tank_number = data.get('tankNumber')
        print(f"TANK NUMBER: {tank_number}")
        device_id = data.get('device_id', 'raspi-001')
    else:
        print("GOT GET REQUEST")

        pad = request.args.get('pad')
        device_id = request.args.get('device_id', 'raspi-001')

    pad = sanitize_pad(pad)
    if pad is None:
        return jsonify({'error': 'Pad must be a positive integer'}), 400

    # Secure file search—match padN.mp3 only, avoid pad10.mp3 for pad1
    mp3_file = None
    for fname in os.listdir(MP3_FOLDER):
        if fname.endswith('.mp3') and re.match(rf'^{pad}\b.*\.mp3$', fname):
            mp3_file = os.path.join(MP3_FOLDER, fname)
            break

    if not mp3_file or not os.path.isfile(mp3_file):
        return jsonify({'error': f'No MP3 found for pad {pad}'}), 404

    # Firebase command (only for POST)
    if request.method == 'POST':
        try:
            command_data = {
                'action': 'play_pad',
                'pad': pad,
                'tank_number': tank_number,
                'timestamp': int(time.time())
            }
            command_ref = db.reference(f'commands/{device_id}')
            command_ref.set(command_data)
        except Exception as e:
            return jsonify({'error': 'Device command failed', 'details': str(e)}), 500

    mime_type, _ = mimetypes.guess_type(mp3_file)
    return send_file(mp3_file, mimetype=mime_type or 'audio/mpeg')

def stress_test_play_pad(device_id='raspi-001'):
    """
    Continuously sends a play_pad command to the db every second
    with a random integer from 1 to 40 as the pad value.
    This function runs forever until the process is killed.
    """
    print(f"Starting stress test for device {device_id}. Press Ctrl+C to stop.")
    count = 0
    while True:
        pad = random.randint(1, 40)
        command_data = {
            'action': 'play_pad',
            'pad': pad,
            'timestamp': int(time.time())
        }
        try:
            command_ref = db.reference(f'commands/{device_id}')
            command_ref.set(command_data)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent play_pad for pad {pad} to device {device_id}")
        except Exception as e:
            print(f"Error sending play_pad for pad {pad}: {e}")
        count += 1
        time.sleep(1)

@app.route('/stop_sounds', methods=['POST'])
def stop_sounds():
    data = request.json
    device_id = data.get('device_id')
    if not device_id:
        return jsonify({'error': 'Missing device_id'}), 400

    # Send command to Firebase
    command_data = {
        'action': 'stop_sounds'
    }
    command_ref = db.reference(f'commands/{device_id}')
    command_ref.set(command_data)

    return jsonify({'status': 'Stop sounds command sent'})

@app.route('/set_tank_level', methods=['POST'])
def set_tank_level():
    data = request.json
    device_id = data.get('device_id')
    tank_id = data.get('tank_id')
    level = data.get('level')
    if not device_id or tank_id not in [1, 2, 3] or level is None:
        return jsonify({'error': 'Invalid input'}), 400

    # Send command to Firebase
    command_data = {
        'action': 'set_tank_level',
        'tank_id': tank_id,
        'level': level
    }
    command_ref = db.reference(f'commands/{device_id}')
    command_ref.set(command_data)

    return jsonify({'status': f'Tank {tank_id} level set to {level}'})

if __name__ == '__main__':
    # To run the stress test, uncomment the following line:
    # stress_test_play_pad('raspi-001')
    app.run(host='0.0.0.0', port=5000, threaded=False)
