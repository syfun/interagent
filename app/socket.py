import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


@sio.on('chat')
async def chat_message(sid, data):
    await sio.emit('chat', data)
