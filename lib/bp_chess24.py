# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_HTML, CHESS960
from lib.bp_interface import InternetGameInterface

import re
import chess


# Chess24.com
class InternetGameChess24(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/chess24\.com\/[a-z]+\/(analysis|game|download-game)\/([a-z0-9\-_]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Chess24.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if len(gid) == 22:
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Download the page
        if self.id is None:
            return None
        url = 'https://chess24.com/en/game/%s' % self.id
        page = self.download(url, userAgent=True)  # Else HTTP 403 Forbidden
        if page is None:
            return None

        # Extract the JSON of the game
        lines = page.split("\n")
        for line in lines:
            line = line.strip()
            pos1 = line.find('.initGameSession({')
            pos2 = line.find('});', pos1)
            if -1 in [pos1, pos2]:
                continue

            # Read the game from JSON
            bourne = self.json_loads(line[pos1 + 17:pos2 + 1])
            chessgame = self.json_field(bourne, 'chessGame')
            moves = self.json_field(chessgame, 'moves')
            if '' in [chessgame, moves]:
                continue

            # Build the header of the PGN file
            game = {}
            game['_moves'] = ''
            game['_url'] = url
            game['Event'] = self.json_field(chessgame, 'meta/Event')
            game['Site'] = self.json_field(chessgame, 'meta/Site')
            game['Date'] = self.json_field(chessgame, 'meta/Date')
            game['Round'] = self.json_field(chessgame, 'meta/Round')
            game['White'] = self.json_field(chessgame, 'meta/White/Name')
            game['WhiteElo'] = self.json_field(chessgame, 'meta/White/Elo')
            game['Black'] = self.json_field(chessgame, 'meta/Black/Name')
            game['BlackElo'] = self.json_field(chessgame, 'meta/Black/Elo')
            game['Result'] = self.json_field(chessgame, 'meta/Result')

            # Build the PGN
            board = chess.Board(chess960=True)
            head_complete = False
            for move in moves:
                # Info from the knot
                kid = self.json_field(move, 'knotId')
                if kid == '':
                    break
                kmove = self.json_field(move, 'move')

                # FEN initialization
                if kid == 0:
                    kfen = self.json_field(move, 'fen')
                    if kfen == '':
                        break
                    try:
                        board.set_fen(kfen)
                    except Exception:
                        return None
                    game['Variant'] = CHESS960
                    game['SetUp'] = '1'
                    game['FEN'] = kfen
                    head_complete = True
                else:
                    if not head_complete:
                        return None

                    # Execution of the move
                    if kmove == '':
                        break
                    try:
                        kmove = chess.Move.from_uci(kmove)
                        game['_moves'] += board.san(kmove) + ' '
                        board.push(kmove)
                    except Exception:
                        return None

            # Rebuild the PGN game
            return self.rebuild_pgn(game)
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chess24.com/en/game/DQhOOrJaQKS31LOiOmrqPg#anchor', True),    # Game with anchor
                ('https://CHESS24.com', False)]                                         # Not a game (homepage)
