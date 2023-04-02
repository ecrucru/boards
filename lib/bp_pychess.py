# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_WS
from lib.bp_interface import InternetGameInterface
from lib.ws import InternetWebsockets


# Pychess.org
class InternetGamePychess(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'https?:\/\/(www\.)?pychess(-variants\.herokuapp\.com|\.org)\/([a-z0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Pychess.org', BOARD_CHESS, METHOD_WS

    def assign_game(self, url: str) -> bool:
        # Retrieve the ID of the game
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) == 8:
                self.id = gid
                return True

        # Nothing found
        return False

    async def download_game(self) -> Optional[str]:
        result = None
        data = None
        if self.id is not None:
            # Open a websocket to retrieve the game
            ws = await InternetWebsockets().connect('wss://www.pychess.org/wsr')
            try:
                await ws.send('{"type":"board","gameId":"%s"}' % self.id)
                for _ in range(5):
                    async for data in ws.recv():
                        data = self.json_loads(data)
                    if data is not None:
                        if data['type'] == 'board' and data['gameId'] == self.id:
                            result = data['pgn'] if data['pgn'] != '' else None
                            break
            finally:
                await ws.close()
        return result

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://pychess.org/DGN5Ps2k#tag', True),                  # Crazyhouse
                ('http://pychess-variants.herokuapp.com/uWbgRNfw', True),   # Chess
                ('http://PYCHESS.org/4XTiOuKB', True),                      # Chess960
                ('http://pychess.ORG/b8aZwvoJ', True),                      # Placement
                ('https://pychess.org/drtDbEhd#tag', True),                 # Shogi
                ('https://pychess.ORG/tALxtipo', True),                     # Makruk
                ('https://pychess.org/2CKjayxv?param', True),               # Cambodian
                ('https://PYCHESS.ORG/4x0kQ8kY', True),                     # Sittuyin
                ('https://pychess.org/7cqV5j2N', True),                     # Seirawan
                ('https://pychess.org/bEh4x0XT', False),                    # Not a game (invalid identifier)
                ('http://pychess.org', False)]                              # Not a game (homepage)
