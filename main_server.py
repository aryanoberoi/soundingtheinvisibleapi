import os
import base64
from flask import Flask
from flask_socketio import SocketIO, emit
from pythonosc import udp_client
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

MP3_FOLDER = 'webfiles'  

@socketio.on('play_pad')
def handle_play_pad(data):
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
            with open(mp3_file, 'rb') as f:
                mp3_bytes = f.read()
            mp3_b64 = base64.b64encode(mp3_bytes).decode('utf-8')
            emit('mp3_file', {'filename': os.path.basename(mp3_file), 'data': mp3_b64})
        else:
            emit('mp3_file', {'error': f'No MP3 found for pad {pad}'})

@socketio.on('stop_sounds')
def handle_stop_sounds():
    osc_client.send_message('/2/stop', [1])

@socketio.on('set_tank_level')
def handle_set_tank_level(data):
    tank_id = data.get('tank_id')
    level = data.get('level')
    if tank_id in [1,2,3] and level is not None:
        osc_address = f'/1/fader{tank_id}'
        osc_client.send_message(osc_address, [level])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)