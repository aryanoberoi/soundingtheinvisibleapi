import os
import re
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mimetypes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
        data = request.json or {}
        pad = data.get('pad')
        device_id = data.get('device_id', 'raspi-001')
    else:
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

    # Firebase command
# Firebase command (only for POST)
    if request.method == 'POST':
        try:
            command_data = {
                'action': 'play_pad',
                'pad': pad
            }
            command_ref = db.reference(f'commands/{device_id}')
            command_ref.set(command_data)
        except Exception as e:
            return jsonify({'error': 'Device command failed', 'details': str(e)}), 500

    mime_type, _ = mimetypes.guess_type(mp3_file)
    return send_file(mp3_file, mimetype=mime_type or 'audio/mpeg')

if __name__ == "__main__":
    app.run(debug=True)


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
