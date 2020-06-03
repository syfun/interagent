import socketio

sio = socketio.AsyncServer(async_mode='asgi')


@sio.on('chat message')
async def chat_message(sid, data):
    await sio.emit('chat message', data)

