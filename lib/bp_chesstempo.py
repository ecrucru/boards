# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from base64 import b64decode

from lib.const import BOARD_CHESS, METHOD_WS, TYPE_GAME, TYPE_PUZZLE
from lib.bp_interface import InternetGameInterface
from lib.ws import InternetWebsockets


# ChessTempo.com
class InternetGameChesstempo(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'game': re.compile(r'^https?:\/\/(\S+\.)?chesstempo\.com\/gamedb\/game\/(\d+)', re.IGNORECASE),
                             'puzzle': re.compile(r'^https?:\/\/(\S+\.)?chesstempo\.com\/chess-tactics\/(\d+)', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessTempo.com', BOARD_CHESS, METHOD_WS

    def assign_game(self, url: str) -> bool:
        # Puzzles
        m = self.regexes['puzzle'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.url_type = TYPE_PUZZLE
                return True

        # Games
        m = self.regexes['game'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.url_type = TYPE_GAME
                return True
        return False

    async def download_game(self) -> Optional[str]:
        # Check
        if None in [self.id, self.url_type]:
            return None

        # Games
        if self.url_type == TYPE_GAME:
            pgn = self.download('http://old.chesstempo.com/requests/download_game_pgn.php?gameids=%s' % self.id)
            if pgn is None or len(pgn) <= 128:
                return None
            return pgn

        # Puzzles
        if self.url_type == TYPE_PUZZLE:

            # Open a websocket to retrieve the puzzle
            data = None
            ws = await InternetWebsockets().connect('wss://chesstempo.com:443/ws', headers=[('User-agent', self.user_agent)])
            try:
                # Check the welcome message
                buffer = None
                async for buffer in ws.recv():
                    buffer = self.json_loads(buffer)
                if (buffer['eventName'] == 'connectionStarted') and (buffer['data'] == 'started'):

                    # Call the puzzle
                    await ws.send('{"eventName":"get-problem-session-data","data":{"problemSetId":1,"sessionSize":20}}')
                    await ws.send('{"eventName":"set-problem-difficulty","data":{"difficulty":"","problemSetId":1}}')
                    await ws.send('{"eventName":"get-tactic","data":{"problemId":%s,"vo":false}}' % self.id)

                    for _ in range(3):
                        async for buffer in ws.recv():
                            buffer = self.json_loads(buffer)
                        if buffer['eventName'] == 'get-tactic-result':
                            if buffer['enc']:
                                buffer = ''.join(map(lambda v: v if v < '0' or v > '9' else str((9 + int(v)) % 10), list(buffer['data'])))
                                data = b64decode(buffer).decode().strip()
                            else:
                                data = buffer['data'].strip()
            finally:
                await ws.close()
            if data in [None, '']:
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

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chesstempo.com/gamedb/game/2046457', True),                       # Game
                ('https://CHESSTEMPO.com/gamedb/game/2046457/foo/bar/123', True),           # Game with additional path
                ('https://www.chesstempo.com/gamedb/game/2046457?p=0#tag', True),           # Game with additional parameters
                ('https://old.chesstempo.com/gamedb/game/2046457', True),                   # Game with archived URL
                ('https://en.chesstempo.com/chess-tactics/71360', True),                    # Puzzle
                ('http://chesstempo.com/faq.html', False)]                                  # Not a game
