import paho.mqtt.client as mqtt
import msgpack


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/bfe8a4c4-2947-4e01-a2d9-b8bde08dfba6/ad")
    client.subscribe("11")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic + " " + msgpack.unpackb(msg.payload))
    print(client, userdata, msg.topic, '1111', str(msg.payload))
    print('123123', msgpack.unpackb(msg.payload))


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
