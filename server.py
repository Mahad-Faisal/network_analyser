from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

def run_netsh_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def get_windows_wifi_data():
    wifi_data = {}
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.splitlines()
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if 'SSID' in line and 'BSSID' not in line:  # To avoid BSSID being caught as SSID
                wifi_data['SSID'] = line.split(':', 1)[1].strip()
            elif 'Signal' in line:
                wifi_data['Signal Strength'] = line.split(':', 1)[1].strip()
            elif 'BSSID' in line:
                wifi_data['BSSID'] = line.split(':', 1)[1].strip()
            elif 'Network type' in line:
                wifi_data['Network Type'] = line.split(':', 1)[1].strip()
            elif 'Radio type' in line:
                wifi_data['Radio Type'] = line.split(':', 1)[1].strip()
            elif 'Authentication' in line:
                wifi_data['Authentication'] = line.split(':', 1)[1].strip()
            elif 'Cipher' in line:
                wifi_data['Cipher'] = line.split(':', 1)[1].strip()
            elif 'Band' in line:
                wifi_data['Band'] = line.split(':', 1)[1].strip()
            elif 'Channel' in line:
                wifi_data['Channel'] = line.split(':', 1)[1].strip()
            elif 'Receive rate' in line:
                wifi_data['Receive Rate'] = line.split(':', 1)[1].strip()
            elif 'Transmit rate' in line:
                wifi_data['Transmit Rate'] = line.split(':', 1)[1].strip()
            elif 'Profile' in line:
                wifi_data['Profile'] = line.split(':', 1)[1].strip()
    except subprocess.CalledProcessError:
        wifi_data['error'] = 'Failed to fetch Wi-Fi data'
    return wifi_data

def get_visible_networks():
    networks = []
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.splitlines()
        current_network = {}
        for line in lines:
            line = line.strip()  # Clean up leading/trailing spaces
            if 'SSID' in line and 'BSSID' not in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'SSID': line.split(':', 1)[1].strip()}
            elif 'Signal' in line:
                current_network['Signal Strength'] = line.split(':', 1)[1].strip()
            elif 'Channel' in line:
                current_network['Channel'] = line.split(':', 1)[1].strip()
        if current_network:
            networks.append(current_network)
    except subprocess.CalledProcessError:
        networks.append({'error': 'Failed to fetch visible networks'})
    return networks

@app.route('/api/wifi')
def wifi():
    return jsonify(get_windows_wifi_data())

@app.route('/api/networks')
def networks():
    return jsonify(get_visible_networks())

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
