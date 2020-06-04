import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')
    sio.emit('chat_message', {'response': 'my response'})


@sio.event
def chat_message(data):
    print('message received with ', data)
    sio.emit('chat_message', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')


sio.connect('http://localhost:8000')
sio.wait()
