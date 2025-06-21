# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2025 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from base64 import b64decode
import chess

from lib.const import BOARD_CHESS, METHOD_WS, TYPE_GAME, TYPE_PUZZLE
from lib.bp_interface import InternetGameInterface
from lib.ws import InternetWebsockets


# ChessTempo.com
class InternetGameChesstempo(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'game': re.compile(r'^https?:\/\/(\S+\.)?chesstempo\.com\/game-database\/game(\/[\w-]+)?\/(\d+)', re.IGNORECASE),
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
            gid = str(m.group(3))
            if gid.isdigit() and (gid != '0'):
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
            # Read the JSON
            data = self.download('https://chesstempo.com/game-database/game/%s' % self.id)
            p1 = data.find('{', data.find('ct-config-data'))
            p2 = data.find('</script>', p1)
            if -1 in [p1, p2]:
                return None
            bourne = data[p1:p2].strip()
            chessgame = self.json_loads(bourne)['gameData']

            # Header
            game = {'Site': self.json_field(chessgame, 'site'),
                    'Event': self.json_field(chessgame, 'event'),
                    'Date': self.json_field(chessgame, 'date'),
                    'White': self.json_field(chessgame, 'white'),
                    'WhiteElo': self.json_field(chessgame, 'elowhite'),
                    'Black': self.json_field(chessgame, 'black'),
                    'BlackElo': self.json_field(chessgame, 'eloblack'),
                    'Round': self.json_field(chessgame, 'round'),
                    'ECO': self.json_field(chessgame, 'eco'),
                    'Opening': self.json_field(chessgame, 'opening_name')}
            tmp = self.json_field(chessgame, 'result')
            if tmp == 'w':
                game['Result'] = '1-0'
            elif tmp == 'b':
                game['Result'] = '0-1'
            else:
                game['Result'] = '1/2-1/2'
            tmp = self.json_field(chessgame, 'start_pos')
            if tmp != '':
                game['SetUp'] = '1'
                game['FEN'] = tmp

            # Body
            moves = self.json_field(chessgame, 'moves_lalg')
            game['PlyCount'] = len(moves)
            game['_moves'] = ''
            board = chess.Board(chess960=True)
            if 'FEN' in game:
                board.set_fen(game['FEN'])
            for move in moves:
                try:
                    kmove = chess.Move.from_uci(move)
                    game['_moves'] += board.san(kmove) + ' '
                    board.push(kmove)
                except Exception:
                    return None
            return self.rebuild_pgn(game)

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
        return [('https://chesstempo.com/game-database/game/2046457', True),                # Game
                ('https://CHESSTEMPO.com/game-database/game/2046457/foo/bar/123', True),    # Game with additional path
                ('https://www.chesstempo.com/game-database/game/2046457?p=0#tag', True),    # Game with additional parameters
                ('https://old.chesstempo.com/game-database/game/2046457', True),            # Game with archived URL
                ('https://en.chesstempo.com/chess-tactics/71360', True),                    # Puzzle
                ('http://chesstempo.com/faq.html', False)]                                  # Not a game
