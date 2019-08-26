import asyncio
from aiohttp import web, WSMsgType
import os
import aiohttp_jinja2
import jinja2

class Client(object):
    def __init__(self, id, ws):
        self.id = id
        self.ws = ws

class WSHandler:

    def __init__(self):
        self.ws_list = set()

    @aiohttp_jinja2.template('index.html')
    def index_handler(self, request):
        return

    async def ws_handler(self, request):
        """
            - CONN*ruben
            - MESG*hey hey
            - CLOSE
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        client = Client('anonymous', ws)
        self.ws_list.add(client)
        print('Websocket connection ready')
        print('Total clients: ' + str(len(self.ws_list)))
        await self._send_user_list()
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                type_msg = msg.data[:4]
                message = msg.data[5:]
                if type_msg == 'CONN':
                    client.id = message
                    await client.ws.send_str('OK')
                    await self._send_user_list()
                else:
                    for c in self.ws_list:
                        await c.ws.send_str('MESG*{}: {}'.format(client.id, message))
            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                    ws.exception())
        self.ws_list.remove(client)
        print("Removing... " + str(len(self.ws_list)))
        return ws

    async def _send_user_list(self):
        token = '****'.join([c.id for c in self.ws_list if c.id])
        for c in self.ws_list:
            await c.ws.send_str('LIST*{}'.format(token))
        return

handler = WSHandler()
app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.dirname(os.path.realpath(__file__))))
app.router.add_get('/', handler.index_handler)
app.router.add_get('/ws', handler.ws_handler)
web.run_app(app)










