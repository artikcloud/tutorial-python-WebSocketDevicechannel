#!/usr/bin/env python

"""Sample WebSocket connection to ARTIK Cloud Device channel.

wss://api.artik.cloud/v1.1/websocket

Please see readme for more info:
https://github.com/artikcloud/tutorial-python-WebSocketDevicechannel/blob/master/readme.md

"""


import json
import time
import sys
import asyncio
import websockets

# See `websockets` documentation for more information on usage
# https://websockets.readthedocs.io/en/stable/intro.html

with open('config.json') as json_data:
    CONFIG = json.load(json_data)

DEVICE_ID = CONFIG['device_id']
DEVICE_TOKEN = CONFIG['device_token']

CONNECTION_URL = 'wss://api.artik.cloud/v1.1/websocket?ack=true'

"""
Example:
    wss://api.artik.cloud/v1.1/websocket?ack=true

Documentation:
   https://developer.artik.cloud/documentation/api-reference/websockets-api.html#device-channel-websocket

"""

async def start():

    """This function is called once from asyncio event loop
    and requires python >= 3.5 using the new syntax support with the async def and await statements 

    Details: 
    
        In this sample, we listen for messages of type action ("setOn" or "setOff").

        Upon receiving the action, we also send a message back to the cloud to
        update the device "state" field.

    """

    print("\nConnecting to: ", CONNECTION_URL)

    async with websockets.connect(CONNECTION_URL) as websocket:
        #establish a connection and send the registration payload

        print("\nWebsocket connection is open ... ")

        registration = {
            'type': 'register',
            'sdid': DEVICE_ID,
            'authorization': 'bearer ' + DEVICE_TOKEN,
        }

        print("\nSending register message payload:\n ", json.dumps(registration))

        await send_message(websocket, registration)

        """Upon successful registration you will receive an OK message

        {"data":{"code":"200","message":"OK"}}

        """

        while True:

            received_message = await websocket.recv()

            print("< Received message: {}".format(received_message))

            message = json.loads(received_message)

            if 'type' in message and message['type'] == 'action':
                # handle action sent to device and update state back to cloud
                asyncio.ensure_future(handle_action(websocket, message))

async def handle_action(websocket, message):

    """This handles actions sent to this device and sends state back to cloud.

    Example received message of type = action

    > Received message with data:
    > {"type":"action","cts":...,"ts":...,"mid":"...","sdid":"4b2108...","ddid":"4b2108...",
        "data":{"actions":[{"name":"setOn"}]},
        "ddtid":"dtd1d3...","uid":"e03d44...","boid":"dfef0b...","mv":1}
    
    """

    action = message['data']['actions'][0]
    # the action is available inside a single array element

    payload = {
        'sdid': DEVICE_ID,
        'data': {},
        'cid': 'id-' + str(int(time.time()))
    }

    """Payload for sending message

    Parameters
    ----------
    sdid: String
        Device ID
    data: Object
        Key/Value fields for the device
    cid: String
        client id that is returned if `ack=true` for the connection
    """

    if action['name'] == "setOn":
        payload['data']['state'] = True
        await send_message(websocket, payload)

    elif action['name'] == "setOff":
        payload['data']['state'] = False
        await send_message(websocket, payload)

    else:
        #unknown action for handling
        print("Unknown action for handing {}".format(action))


async def send_message(websocket, message):

    """Send message via websocket to cloud to update device fields

    Example message payload:

        {"sdid": "4b2108...", "data": {"state": true}, "cid": 1501787234}

    """

    message = json.dumps(message)
    print("> Sending Message: {}".format(message))
    await websocket.send(message)

try:
    asyncio.get_event_loop().run_until_complete(start())
except KeyboardInterrupt as error:
    print("\nApplication Exited. {0}".format(error))
else:
    print("Unknown Error '{0}'".format(sys.exc_info()[0]))
