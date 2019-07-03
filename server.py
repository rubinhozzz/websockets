import asyncio
from aiohttp import web, WSMsgType
import os

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))
clients = []

class Client(object):
    def __init__(self, id, ws):
        self.id = id
        self.ws = ws

async def ws_handler(request):
    print('Websocket connection starting')
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client = Client('anonymous', ws)
    clients.append(client)
    print('Websocket connection ready')
    # send list of all clients
    await _send_user_list() 
    async for msg in client.ws:
        """
        - CONN*ruben
        - MESG*hey hey
        - CLOSE
        """
        print(msg)
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'CLOSE':
                await client.ws.close()
                return ws
            type_msg = msg.data[:4]
            message = msg.data[5:]
            if type_msg == 'CONN':
                client.id = message
                await client.ws.send_str('OK')
                await _send_user_list()
            else:
                for c in clients:
                    await c.ws.send_str('MESG*{}: {}'.format(client.id, message))
    clients.remove(client)
    return ws

async def _send_user_list():
    token = '****'.join([c.id for c in clients if c.id])
    for c in clients:
        await c.ws.send_str('LIST*{}'.format(token))
    return

def main():
    loop = asyncio.get_event_loop()
    app = web.Application()
    app.add_routes([
        web.get('/ws', ws_handler),
    ])
    web.run_app(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()


