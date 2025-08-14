import serial
import os
from pythonosc import udp_client

# Open serial port
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

left_vol = 100.0
right_vol = 100.0

def clamp(value):
    return max(0.0, min(1.0, value))

def set_channel_volume(channel: str, value: int):
    global left_vol, right_vol

    norm = clamp(value / 100.0)

    if channel == 'L':
        left_vol = norm
    elif channel == 'R':
        right_vol = norm
    else:
        return

    left_address = f'/1/fader4'
    right_address = f'/1/fader5'
    osc_client.send_message(left_address, [left_vol])
    osc_client.send_message(right_address, [right_vol])
    print(f"Set volume: Baseline={int(left_vol * 100)}%, Pollutant={int(right_vol * 100)}%")


print("Listening on /dev/ttyAMA0...")

try:
    while True:
        line = ser.readline().decode().strip()
        if line.upper() == 'S':
            print("Shutdown command received.")
            os.system("sudo shutdown now")
            break  # Optional: exit loop after issuing shutdown
        elif ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                command = parts[0].upper()
                try:
                    value = int(parts[1])
                    set_channel_volume(command, value)
                except ValueError:
                    print(f"Ignored invalid value: {parts[1]}")
except KeyboardInterrupt:
    print("Exiting.")
finally:
    ser.close()
