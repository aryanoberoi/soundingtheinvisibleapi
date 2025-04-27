import os
import base64
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

app = Flask(__name__)

MP3_FOLDER = 'webfiles'  # Your local MP3 folder

# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://soundingtheinvisible-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your actual Firebase DB URL
})

@app.route('/play_pad', methods=['POST'])
def play_pad():
    data = request.json
    device_id = data.get('device_id')
    pad = data.get('pad')
    if not device_id or pad is None:
        return jsonify({'error': 'Missing device_id or pad'}), 400

    # 1. Serve MP3 file
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

    # 2. Send command to Firebase
    command_data = {
        'action': 'play_pad',
        'pad': pad
    }
    command_ref = db.reference(f'commands/{device_id}')
    command_ref.set(command_data)

    return jsonify(mp3_response)

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
