from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from threading import Lock

import Client
t = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()
tmp = True

def background_thread():
    while True:
        socketio.sleep(5)
        # emit('my response', {'data': 'Connected'})
        global tmp
        if tmp == True:
            tmp = False
        else :
            tmp = True
            
        socketio.emit('my response',
                      {'ip': '192.168.0.1', 'content': 'We are immortals', 'fromOthers': tmp})

@app.route('/')
def index():
    return render_template('GClient.html')

@socketio.on('my event', namespace='')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event', namespace='')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect', namespace='')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my response', {'ip': '192.168.0.1', 'content': 'We are immortals'})
    print("Someone is connected")

@socketio.on('disconnect', namespace='')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)