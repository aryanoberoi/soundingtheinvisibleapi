import os
import base64
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
from flask_cors import CORS
import mimetypes
from flask import send_file
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all CORS for the Flask app

MP3_FOLDER = 'webfiles'  # Your local MP3 folder

# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://soundingtheinvisible-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your actual Firebase DB URL
})

@app.route('/play_pad', methods=['GET', 'POST'])
def play_pad():
    if request.method == 'POST':
        data = request.json
        pad = data.get('pad')
        device_id = data.get('device_id')
    else:  # GET method
        pad = request.args.get('pad', type=int)
        device_id = request.args.get('device_id', 'raspi-001')

    if pad is None:
        return jsonify({'error': 'Pad not specified'}), 400

    # 1. Find MP3 file
    mp3_file = None
    for fname in os.listdir(MP3_FOLDER):
        if fname.endswith('.mp3') and str(pad) in fname:
            mp3_file = os.path.join(MP3_FOLDER, fname)
            break

    if not mp3_file or not os.path.isfile(mp3_file):
        return jsonify({'error': f'No MP3 found for pad {pad}'}), 404

    command_data = {
        'action': 'play_pad',
        'pad': pad,
        'timestamp': int(time.time() * 1000)  # <- add this
    }
    command_ref = db.reference(f'commands/{device_id}')
    command_ref.set(command_data)

    # 3. Return actual mp3 file (directly)
    mime_type, _ = mimetypes.guess_type(mp3_file)
    return send_file(mp3_file, mimetype=mime_type or 'audio/mpeg')


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
    app.run(host='0.0.0.0', port=5000, threaded=True)
