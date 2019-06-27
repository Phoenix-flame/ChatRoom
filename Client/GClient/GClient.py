from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
from threading import Lock


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


def background_thread():
    while True:
        socketio.sleep(5)
        # emit('my response', {'data': 'Connected'})
        socketio.emit('my response',
                      {'data': 'We are Immortals...'})

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
    emit('my response', {'data': 'Connected'})
    print("Someone is connected")

@socketio.on('disconnect', namespace='')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)