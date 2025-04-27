import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://soundingtheinvisible-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('device_id')
    action = data.get('action')
    payload = data.get('payload', {})

    if not device_id or not action:
        return jsonify({'error': 'Missing device_id or action'}), 400

    command_data = {
        'action': action,
        **payload
    }
    command_ref = db.reference(f'commands/{device_id}')
    command_ref.set(command_data)

    return jsonify({'status': 'Command sent'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
