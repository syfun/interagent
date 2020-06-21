import json
import logging
import logging.config

import requests
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import settings
from app.db.models import Ad


logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/5c2ef8c4-cc04-4844-b78a-eac31c3c08ec/ad")


def download_file(filename, url):
    logger.info(f'download file {filename}')
    filename = str(settings.ROOT_DIR / 'media' / filename)
    logger.info(f'############### {filename}')
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    ad = json.loads(msg.payload)
    logger.info(f'Received messgae: {msg.topic}, ad: {ad}')
    action, data = ad.get('action'), ad.get('data', {})
    if action not in ['edit', 'delete']:
        logger.info(f"skip action {action}, expect 'edit' or 'delete'")
        return

    id = data.get('id')
    if not id:
        return

    if action == 'delete':
        session.query(Ad).filter_by(id=id).delete()
        session.commit()
        return

    ad = session.query(Ad).filter_by(id=id).first()
    download = False
    url = data.pop('url', None)
    if not ad:
        logger.info(f'add new ad: {id}')
        session.add(Ad(**data))
        download = True
        session.commit()
    elif ad.to_dict() != data:
        logger.info(f'update ad: {id}')
        if ad.file != data.get('file'):
            download = True
        ad.file = data.get('file')
        ad.schedule = data.get('schedule')
        session.commit()
    if download:
        download_file(data.get('file'), url)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
# client.message_callback_add('11', on_message)
# client.message_callback_add("device/bfe8a4c4-2947-4e01-a2d9-b8bde08dfba6/ad", on_message)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
