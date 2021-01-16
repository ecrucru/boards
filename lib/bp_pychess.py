# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_WS
from lib.bp_interface import InternetGameInterface

import re
import websockets


# Pychess.org
class InternetGamePychess(InternetGameInterface):
    def get_identity(self):
        return 'Pychess.org', BOARD_CHESS, METHOD_WS

    def assign_game(self, url):
        # Retrieve the ID of the game
        rxp = re.compile(r'https?:\/\/(www\.)?pychess(-variants\.herokuapp\.com|\.org)\/([a-z0-9]+)[\/\?\#]?', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) == 8:
                self.id = gid
                return True

        # Nothing found
        return False

    async def download_game(self):
        # Check
        if self.id is None:
            return None

        # Open a websocket to retrieve the game
        async def coro():
            result = None
            ws = await websockets.connect('wss://www.pychess.org/wsr', origin="https://www.pychess.org", ping_interval=None)
            try:
                await ws.send('{"type":"board","gameId":"%s"}' % self.id)
                for i in range(5):
                    data = await ws.recv()
                    data = self.json_loads(data)
                    if data['type'] == 'board' and data['gameId'] == self.id:
                        result = data['pgn'] if data['pgn'] != '' else None
                        break
            finally:
                await ws.close()
            return result

        data = await coro()
        return data

    def get_test_links(self):
        return [('http://pychess.org/DGN5Ps2k#tag', True),                  # Crazyhouse
                ('http://pychess-variants.herokuapp.com/uWbgRNfw', True),   # Chess
                ('http://PYCHESS.org/4XTiOuKB', True),                      # Chess960
                ('http://pychess.ORG/b8aZwvoJ', True),                      # Placement
                ('https://pychess.org/drtDbEhd#tag', False),                # Shogi (unsupported)
                ('https://pychess.ORG/tALxtipo', True),                     # Makruk
                ('https://pychess.org/2CKjayxv?param', True),               # Cambodian
                ('https://PYCHESS.ORG/4x0kQ8kY', True),                     # Sittuyin
                ('https://pychess.org/7cqV5j2N', True),                     # Seirawan
                ('http://pychess.org', False)]                              # Not a game (homepage)
