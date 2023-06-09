import paho.mqtt.client as mqtt
import json, time, os

num_blocks = 0
file_size = 0
file_name = ""
block_nr = 0

try:
    os.mkdir('images')
except FileExistsError:
    pass
os.chdir('images/')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("proj/images")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global block_nr
    global num_blocks
    global file_name
    global file_size
    
    if b'mqtt_camera_image' in msg.payload:
        
        msg_info = json.loads(msg.payload)
        # print(msg_info)
        msg_type = msg_info["type"]
        file_name = msg_info["file_name"]
        file_size = msg_info["file_size"]
        block_size = msg_info["block_size"]    
        num_blocks = msg_info["num_blocks"]
    
        block_nr = 0

        #deletefile(file_name)    
        print(f"new image. type: {msg_type}, name: {file_name}, \
        size: {file_size}, blocks: {num_blocks}, block size: {block_size}")
    
    else:
        block_nr += 1
          
        with open(file_name, "ab") as f:
            #buf = bytes(file_size)
            print(">>>appending to buffer, block nr. {} ".format(block_nr))
            f.write(msg.payload)
            time.sleep(0.2)
        if  block_nr == num_blocks:
            print("file {} complete".format(file_name))

# deleting file from disk:
def deletefile(filename):
    import os
    if os.path.exists(file_name):
      os.remove(file_name)
      print("deleted file {}".format(file_name))
    else:
      print("File does not exist, nothing deleted")

try:
    client = mqtt.Client()
except Exception as e:
    print(e)

client.connect("192.168.178.36", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
