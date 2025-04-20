import os
from flask import Flask, request, send_file, jsonify
import socketio

app = Flask(__name__)
MP3_FOLDER = 'webfiles'  # Change this if your mp3s are elsewhere

# SocketIO client setup (connects to main_server.py)
sio = socketio.Client()
MAIN_SERVER_URL = os.getenv('MAIN_SERVER_URL')  # Set this environment variable to the correct ws server

# Try to connect to main_server.py at startup, but don't crash if it fails
try:
    sio.connect(MAIN_SERVER_URL)
    print(f"Connected to main_server.py at {MAIN_SERVER_URL}")
except Exception as e:
    print(f"Warning: Could not connect to main_server.py at {MAIN_SERVER_URL}: {e}")

@app.route('/play_pad')
def play_pad():
    pad = request.args.get('pad')
    if pad is None:
        return jsonify({'error': 'pad parameter required'}), 400

    # Try to notify main_server.py via websocket, but continue if it fails
    try:
        sio.emit('play_pad', {'pad': pad})
    except Exception as e:
        print(f"Warning: Could not notify main_server.py via websocket: {e}")

    # Find the mp3 file locally
    mp3_file = None
    for fname in os.listdir(MP3_FOLDER):
        if fname.endswith('.mp3') and str(pad) in fname:
            mp3_file = os.path.join(MP3_FOLDER, fname)
            break

    if mp3_file and os.path.isfile(mp3_file):
        return send_file(mp3_file, mimetype='audio/mpeg', as_attachment=True)
    else:
        return jsonify({'error': f'No MP3 found for pad {pad}'}), 404

# Healthcheck endpoint
@app.route('/healthcheck')
def healthcheck():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(port=5000)