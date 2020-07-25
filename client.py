import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')
    sio.emit('waitTouch', 'wait')


@sio.on('test')
def test(data):
    sio.emit('waitTouch', data


@sio.on('touchStart')
def touch_start(data):
    print('receive touchStart event: ', data)


@sio.on('touchEnd')
def touch_end(data):
    print('receive touchEnd event', data)


@sio.event
def disconnect():
    print('disconnected from server')


sio.connect('http://localhost:8000')
sio.wait()
