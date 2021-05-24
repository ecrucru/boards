# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, Dict, AsyncIterator
import aiohttp
import logging


# Class to handle the websockets as a client via aiohttp following a syntax near to websockets
class InternetWebsockets():
    ''' aiohttp @ https://docs.aiohttp.org/en/stable/client_quickstart.html#websockets
            from lib.ws import InternetWebsockets
            async def main():
                ws = await InternetWebsockets().connect('wss://...')    # Exception if failed
                try:
                    async for data in ws.recv():
                        print(data)
                        # break is mostly useless
                    await ws.send('Hello')
                finally:
                    await ws.close()

        ---
        websockets @ https://websockets.readthedocs.io/en/stable/
            import websockets
            async def main():
                ws = await websockets.connect('wss://...', origin='', ping_interval=None)
                try:
                    data = await ws.recv()
                    await ws.send('Hello')
                finally:
                    await ws.close()
    '''
    def __init__(self):
        self.acs: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.client_ws.ClientWebSocketResponse] = None

    async def connect(self, url: Optional[str], headers: Optional[Dict] = None) -> 'InternetWebsockets':
        if url is not None:
            logging.debug('Websocket connecting to %s' % url)
            self.acs = aiohttp.ClientSession()
            self.ws = await self.acs.ws_connect(url, headers=headers, heartbeat=None)
        return self

    async def recv(self) -> AsyncIterator[Optional[str]]:
        result = None
        if self.ws is not None:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    result = msg.data
                break
        yield result

    async def send(self, data: str) -> None:
        if self.ws is not None:
            await self.ws.send_str(data)

    async def close(self) -> None:
        if self.ws is not None:
            await self.ws.close()
            self.ws = None
        if self.acs is not None:
            await self.acs.close()
            self.acs = None
