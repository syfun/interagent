import logging

import socketio

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


@sio.on('waitTouch')
async def wait_touch(sid, data):
    await sio.emit('waitTouch', 'waitTouch')


@sio.on('touchStart')
async def touch_start(sid, data):
    await sio.emit('touchStart', 'touchStart')


@sio.on('touchEnd')
async def touch_end(sid, data):
    await sio.emit('touchEnd', 'touchEnd')


@sio.on('test')
async def test(sid, data):
    await sio.emit('test', 'test')
