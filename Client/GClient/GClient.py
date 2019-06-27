from flask import render_template
from Client_thread import app, socketio, Client_thread, thread, thread_lock, received_msg, log, emit




def background_thread():
    client = Client_thread()
    client.start()
    while True:
        continue

@app.route('/')
def index():
    return render_template('GClient.html')

@socketio.on('my_event', namespace='')
def test_message(message):
    received_msg.append({'msg': message['data']})
    log.warn('input message' + message['data'])
    socketio.emit('my response', 
                            {'ip': "You:)", 'content': message['data'], 'fromOthers': False})
    

@socketio.on('my broadcast event', namespace='')
def test_message(message):
    print(message['data'])
    
    # emit('my response', {'data': message['data']}, broadcast=True)

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
    
