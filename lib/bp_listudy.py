# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse
import chess


# Listudy.org
class InternetGameListudy(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'Listudy.org', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.listudy.org', 'listudy.org']:
            return False

        # Refactor the direct link
        for key in parsed.path.split('/'):
            if key.isdigit() and (key != '0'):
                self.id = url
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Download
        if self.id is None:
            return None
        page = self.download(self.id)
        if page is None:
            return None

        # Extract the game
        game = {'White': 'White',
                'Black': 'Black'}
        pgn = ''
        lines = page.split('\n')
        for line in lines:
            if 'let pgn =' in line:
                pgn = line.split('"')[1]
            if 'let fen =' in line:
                game['SetUp'] = '1'
                game['FEN'] = line.split('"')[1]
            if ('let solution =' in line) or ('let moves =' in line):
                game['_moves'] = line.split('"')[1]
            if 'i18n.white =' in line:
                game['White'] = line.split('"')[1]
            if 'i18n.black =' in line:
                game['Black'] = line.split('"')[1]

        # Improve the moves
        if pgn != '':                                           # PGN
            game['_moves'] = pgn
        else:
            if game['_moves'].lower() != game['_moves']:        # SAN
                moves = game['_moves'].split(' ')
            else:                                               # UCI
                moves = []
                board = chess.Board(game['FEN'])
                try:
                    for move in game['_moves'].split(' '):
                        kmove = chess.Move.from_uci(move)
                        moves.append(board.san(kmove))
                        board.push(kmove)
                except Exception:
                    return None
            game['_moves'] = '%s (%s)' % (moves[0], ' '.join(moves))

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://listudy.org/en/tactics/382', True),                   # Game
                ('https://listudy.org/en/blind-tactics/406', True),             # Game
                ('https://listudy.org/en/pieceless-tactics/1339', True),        # Game
                ('https://listudy.org/en/endgames/basic/queen/2', False),       # Not a game (endgame)
                ('https://listudy.org', False)]                                 # Not a game (homepage)
