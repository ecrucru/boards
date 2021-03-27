# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_WS, CHESS960
from lib.bp_interface import InternetGameInterface
from lib.ws import InternetWebsockets

import re
import string
from random import choice, randint
import chess


# Chess.org
class InternetGameChessOrg(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/chess\.org\/play\/([a-f0-9\-]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self):
        return 'Chess.org', BOARD_CHESS, METHOD_WS

    def assign_game(self, url):
        m = self.regexes['url'].match(url)
        if m is not None:
            id = str(m.group(1))
            if len(id) == 36:
                self.id = id
                return True
        return False

    def fix_fen(self, fen):
        list = fen.split(' ')
        t = list[2]
        list[2] = t[0] + t[2] + t[1] + t[3]
        return ' '.join(list)

    async def download_game(self):
        # Check
        if self.id is None:
            return None

        # Fetch the page to retrieve the encrypted user name
        url = 'https://chess.org/play/%s' % self.id
        page = self.download(url)
        if page is None:
            return None
        lines = page.split("\n")
        name = ''
        for line in lines:
            pos1 = line.find('encryptedUsername')
            if pos1 != -1:
                pos1 = line.find("'", pos1)
                pos2 = line.find("'", pos1 + 1)
                if pos2 > pos1:
                    name = line[pos1 + 1:pos2]
                    break
        if name == '':
            return None

        # Random elements to get a unique URL
        rndI = randint(1, 1000)
        rndS = ''.join(choice(string.ascii_lowercase) for i in range(8))

        # Open a websocket to retrieve the chess data
        ws = await InternetWebsockets().connect('wss://chess.org:443/play-sockjs/%d/%s/websocket' % (rndI, rndS))
        try:
            # Server: Hello
            async for data in ws.recv():
                if data != 'o':  # Open
                    await ws.close()
                    return None

            # Client: I am XXX, please open the game YYY
            await ws.send('["%s %s"]' % (name, self.id))

            # Server: some data
            async for data in ws.recv():
                if data[:1] != 'a':
                    await ws.close()
                    return None
            data = data[3:-2]
        finally:
            await ws.close()
        if data in [None, '']:
            return None

        # Parses the game
        data = data.replace('\\"', '"')
        chessgame = self.json_loads(data)
        game = {}
        game['_url'] = url

        # Player info
        if self.json_field(chessgame, 'creatorColor') == '1':  # White=1, Black=0
            creator = 'White'
            opponent = 'Black'
        else:
            creator = 'Black'
            opponent = 'White'
        game[creator] = self.json_field(chessgame, 'creatorId')
        elo = self.json_field(chessgame, 'creatorPoint')
        if elo not in ['', '0', 0]:
            game[creator + 'Elo'] = elo
        game[opponent] = self.json_field(chessgame, 'opponentId')
        elo = self.json_field(chessgame, 'opponentPoint')
        if elo not in ['', '0', 0]:
            game[opponent + 'Elo'] = elo

        # Game info
        startPos = self.json_field(chessgame, 'startPos')
        if startPos not in ['', 'startpos']:
            game['SetUp'] = '1'
            game['FEN'] = self.fix_fen(startPos)
            game['Variant'] = CHESS960
            try:
                board = chess.Board(game['FEN'], chess960=True)
            except Exception:
                return None
        else:
            board = chess.Board(chess960=True)
        time = self.json_field(chessgame, 'timeLimitSecs')
        inc = self.json_field(chessgame, 'timeBonusSecs')
        if '' not in [time, inc]:
            game['TimeControl'] = '%s+%s' % (time, inc)
        resultTable = [(0, '*', 'Game started'),                 # ALIVE
                       (1, '1-0', 'White checkmated'),           # WHITE_MATE
                       (2, '0-1', 'Black checkmated'),           # BLACK_MATE
                       (3, '1/2-1/2', 'White stalemated'),       # WHITE_STALEMATE
                       (4, '1/2-1/2', 'Black stalemated'),       # BLACK_STALEMATE
                       (5, '1/2-1/2', 'Insufficient material'),  # DRAW_NO_MATE
                       (6, '1/2-1/2', '50-move rule'),           # DRAW_50
                       (7, '1/2-1/2', 'Threefold repetition'),   # DRAW_REP
                       (8, '1/2-1/2', 'Mutual agreement'),       # DRAW_AGREE
                       (9, '0-1', 'White resigned'),             # WHITE_RESIGN
                       (10, '1-0', 'Black resigned'),            # BLACK_RESIGN
                       (11, '0-1', 'White canceled'),            # WHITE_CANCEL
                       (12, '1-0', 'Black canceled'),            # BLACK_CANCEL
                       (13, '1-0', 'White out of time'),         # WHITE_NO_TIME
                       (14, '0-1', 'Black out of time'),         # BLACK_NO_TIME
                       (15, '*', 'Not started')]                 # NOT_STARTED
        state = self.json_field(chessgame, 'state')
        result = '*'
        reason = 'Unknown reason %d' % state
        for rtID, rtScore, rtMsg in resultTable:
            if rtID == state:
                result = rtScore
                reason = rtMsg
                break
        game['Result'] = result
        game['_reason'] = reason

        # Moves
        game['_moves'] = ''
        moves = self.json_field(chessgame, 'lans')
        if moves == '':
            return None
        moves = moves.split(' ')
        for move in moves:
            try:
                move = chess.Move.from_uci(move)
                game['_moves'] += board.san(move) + ' '
                board.push(move)
            except Exception:  # ValueError
                return None

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self):
        return [('https://chess.org/play/19a8ffe8-b543-4a41-be02-e84e0f4d6f3a', True),      # Classic game
                ('https://CHESS.org/play/c28f1b76-aee0-4577-b8a5-eeda6a0e14af', True),      # Chess960
                ('https://chess.org/play/c28fffe8-ae43-4541-b802-eeda6a4d6f3a', False),     # Not a game (unknown ID)
                ('https://chess.org', False)]                                               # Not a game (homepage)
