import hashlib
import json
import logging
import logging.config
import os

import dataset
import paho.mqtt.client as mqtt
import requests

from app import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)

db = dataset.connect(settings.DATABASE_URL)
ad_table: dataset.Table = db['ads']


def compute_file_checksum(filename):
    with open(filename, 'rb') as f:
        md5 = hashlib.md5()
        while chunk := f.read(2048):
            md5.update(chunk)

        return md5.hexdigest()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f'device/{settings.DEVICE}/ad')
    client.subscribe(f'device/{settings.DEVICE}/config')


def download_file(filename, url, checksum):
    filename = str(settings.ROOT_DIR / 'media' / filename)
    if os.path.exists(filename):
        if checksum == compute_file_checksum(filename):
            logger.info(f'{filename} exists, skip download')
            return

    logger.info(f'start download file to {filename}')
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    logger.info(f'end download file to {filename}')


def delete_file(filename):
    filename = str(settings.ROOT_DIR / 'media' / filename)
    logger.info(f'delete file {filename}')
    if os.path.exists(filename):
        os.remove(filename)
        logger.info(f'delete file {filename} success')
    else:
        logger.info(f'{filename} not exists, skip')


def handle_ad(ad: dict):
    logger.info(f'handle ad: {ad}')
    action, data = ad.get('action'), ad.get('data', {})
    if action not in ['edit', 'delete']:
        logger.info(f"skip action {action}, expect 'edit' or 'delete'")
        return

    id = data.get('id')
    if not id:
        return

    if action == 'delete':
        ad_table.delete(id=id)
        delete_file(data.get('file'))
        return

    ad = ad_table.find_one(id=id)
    new_ad = dict(
        id=id,
        file=data.get('file'),
        schedule=data.get('schedule'),
        default=data.get('default', False),
    )
    if not ad:
        logger.info(f'add new ad: {id}')
        ad_table.insert(new_ad)
    else:
        logger.info(f'update ad: {id}')
        if ad['file'] != new_ad['file']:
            delete_file(ad['file'])
        ad_table.update(new_ad, ['id'])
    download_file(data.get('file'), data.get('url'), data.get('checksum'))


def handle_device_config(data: dict):
    logger.info(f'Handle device config: {data}')
    if not data:
        return

    with open('./device.json', 'w') as f:
        json.dump(data, f)


# The callback for when a PUBLISH message is received from the server.
def _on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    logger.info(f'Received messgae: {msg.topic}')
    if msg.topic.endswith('ad'):
        handle_ad(data)
    elif msg.topic.endswith('config'):
        handle_device_config(data)


def on_message(client, userdata, msg):
    try:
        _on_message(client, userdata, msg)
    except Exception as exc:
        logger.error(str(exc))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
# client.message_callback_add('11', on_message)
# client.message_callback_add("device/bfe8a4c4-2947-4e01-a2d9-b8bde08dfba6/ad", on_message)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
