
from pythonosc import udp_client


# Configure the OSC client
osc_client = udp_client.SimpleUDPClient('127.0.0.1', 57120)  # SuperCollider's default port

def play_sound():
    freq = 440
    amp = 0.5
    osc_client.send_message('/triggerSynth', [freq, amp])
    return 'Sound triggered', 200

play_sound()
