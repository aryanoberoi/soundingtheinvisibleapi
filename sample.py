from pythonosc import udp_client
import time

# Connect to SuperCollider's OSC server
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)

# Trigger sound 6
osc_client.send_message('/2/push6', [1])
print("Triggered sound 6")
time.sleep(1)  # Wait for 1 second

# Trigger sound 7
osc_client.send_message('/2/push7', [1])
print("Triggered sound 7")