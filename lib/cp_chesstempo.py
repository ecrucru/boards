# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_WS, TYPE_GAME, TYPE_PUZZLE
from lib.cp_interface import InternetGameInterface

import re
import websockets
from base64 import b64decode


# ChessTempo.com
class InternetGameChesstempo(InternetGameInterface):
    def get_identity(self):
        return 'ChessTempo.com', BOARD_CHESS, METHOD_WS

    def assign_game(self, url):
        # Puzzles
        rxp = re.compile(r'^https?:\/\/(\S+\.)?chesstempo\.com\/chess-tactics\/(\d+)', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.url_type = TYPE_PUZZLE
                return True

        # Games
        rxp = re.compile(r'^https?:\/\/(\S+\.)?chesstempo\.com\/gamedb\/game\/(\d+)', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.url_type = TYPE_GAME
                return True
        return False

    async def download_game(self):
        # Check
        if None in [self.id, self.url_type]:
            return None

        # Games
        if self.url_type == TYPE_GAME:
            pgn = self.download('http://chesstempo.com/requests/download_game_pgn.php?gameids=%s' % self.id, userAgent=True)  # Else a random game is retrieved
            if pgn is None or len(pgn) <= 128:
                return None
            else:
                return pgn

        # Puzzles
        elif self.url_type == TYPE_PUZZLE:

            # Open a websocket to retrieve the puzzle
            async def coro():
                result = None
                ws = await websockets.connect('wss://chesstempo.com:443/ws', origin='https://chesstempo.com', extra_headers=[('User-agent', self.userAgent)], ping_interval=None)
                try:
                    # Check the welcome message
                    data = await ws.recv()
                    data = self.json_loads(data)
                    if (data['eventName'] == 'connectionStarted') and (data['data'] == 'started'):

                        # Call the puzzle
                        await ws.send('{"eventName":"get-problem-session-data","data":{"problemSetId":1,"sessionSize":20}}')
                        await ws.send('{"eventName":"set-problem-difficulty","data":{"difficulty":"","problemSetId":1}}')
                        await ws.send('{"eventName":"get-tactic","data":{"problemId":%s,"vo":false}}' % self.id)

                        for i in range(3):
                            data = await ws.recv()
                            data = self.json_loads(data)
                            if data['eventName'] == 'get-tactic-result':
                                if data['enc']:
                                    data = ''.join(map(lambda v: v if v < '0' or v > '9' else str((9 + int(v)) % 10), list(data['data'])))
                                    result = b64decode(data).decode().strip()
                                else:
                                    result = data['data'].strip()
                                if result == '':
                                    result = None
                finally:
                    await ws.close()
                return result

            data = await coro()
            if data is None:
                return None

            # Rebuild the puzzle
            puzzle = self.json_loads(data)
            game = {}
            game['_url'] = 'https://chesstempo.com/chess-tactics/%s' % self.id
            game['Event'] = 'Puzzle %s' % self.json_field(puzzle, 'tacticInfo/problem_id')
            game['White'] = 'White'
            game['Black'] = 'Black'
            game['Result'] = '*'
            game['FEN'] = self.json_field(puzzle, 'tacticInfo/startPosition')
            game['SetUp'] = '1'
            game['_moves'] = '{%s} %s' % (self.json_field(puzzle, 'tacticInfo/prevmove'), self.json_field(puzzle, 'tacticInfo/moves'))
            return self.rebuild_pgn(game)

        return None

    def get_test_links(self):
        return [('https://chesstempo.com/gamedb/game/2046457', True),                       # Game
                ('https://CHESSTEMPO.com/gamedb/game/2046457/foo/bar/123', True),           # Game with additional path
                ('https://www.chesstempo.com/gamedb/game/2046457?p=0#tag', True),           # Game with additional parameters
                ('https://en.chesstempo.com/chess-tactics/71360', True),                    # Puzzle
                ('http://chesstempo.com/faq.html', False)]                                  # Not a game
