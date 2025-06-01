import firebase_admin
from firebase_admin import credentials, db
from pythonosc import udp_client
import os
import threading
# Initialize Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://soundingtheinvisible-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase RTDB URL
})

DEVICE_ID = 'raspi-001'  # Unique ID for this Pi
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)
MP3_FOLDER = 'webfiles'

def handle_command(event):
    command_data = event.data
    if not command_data:
        return  # No command, maybe deleted

    action = command_data.get('action')

    if action == 'play_pad':
        import time
        pad = command_data.get('pad')
        timestamp = command_data.get('timestamp')
        current_time = time.time()
        if pad is not None and timestamp is not None:
            # Only send if timestamp is not expired by more than 10 seconds
            if current_time - timestamp <= 10:
                osc_address = f'/2/push{pad}'
                osc_client.send_message(osc_address, [1])
                print(f"Playing pad {pad} at timestamp {timestamp}")
            else:
                print(f"Ignored play_pad for pad {pad}: timestamp {timestamp} expired by more than 10 seconds")

    elif action == 'stop_sounds':
        osc_client.send_message('/2/push16', [1])
        print("Stopping all sounds")

    elif action == 'set_tank_level':
        tank_id = command_data.get('tank_id')
        level = command_data.get('level')
        if tank_id in [1, 2, 3] and level is not None:
            osc_address = f'/1/fader{tank_id}'
            osc_client.send_message(osc_address, [level])
            print(f"Setting tank {tank_id} level to {level}")

def listen_for_commands():
    command_ref = db.reference(f'commands/{DEVICE_ID}')
    command_ref.listen(handle_command)

if __name__ == '__main__':
    listen_for_commands()
