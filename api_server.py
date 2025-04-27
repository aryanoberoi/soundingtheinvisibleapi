# api_server.py
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
main_servers = []

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    ip = data.get('ip')
    if ip:
        if ip not in main_servers:
            main_servers.append(ip)
            print(f"Registered new main server: {ip}")
        return jsonify({'message': 'Registered successfully'}), 200
    return jsonify({'error': 'Invalid IP'}), 400

@app.route('/trigger_all', methods=['POST'])
def trigger_all():
    data = request.json
    action = data.get('action')
    payload = data.get('payload', {})

    results = {}
    for ip in main_servers:
        try:
            url = f"http://{ip}/trigger"
            resp = requests.post(url, json={'action': action, **payload}, timeout=5)
            results[ip] = resp.json()
        except Exception as e:
            results[ip] = str(e)
    return jsonify(results)

def heartbeat_checker():
    while True:
        time.sleep(30)
        for ip in main_servers.copy():
            try:
                resp = requests.get(f"http://{ip}/ping", timeout=5)
                if resp.status_code == 200:
                    print(f"Main server {ip} alive")
                else:
                    print(f"Main server {ip} not responding correctly")
            except:
                print(f"Removing dead main server: {ip}")
                main_servers.remove(ip)

if __name__ == '__main__':
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    app.run(host='0.0.0.0', port=6000, threaded=True)
