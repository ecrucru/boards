# Copyright (C) 2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from math import floor
import chess

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# Immortal.game
class InternetGameImmortal(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/immortal\.game\/games\/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})[\/\?\#]?', re.IGNORECASE)})

    def _str2int(self, value: str) -> int:
        try:
            return round(float(value))
        except ValueError:
            return 0

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Immortal.game', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = str(m.group(1))
            return True
        return False

    def download_game(self) -> Optional[str]:
        # Download the page
        if self.id is None:
            return None
        url = 'https://immortal.game/games/%s' % self.id
        page = self.download(url)
        if page is None:
            return None

        # Extract the JSON of the game
        pos1 = page.find('window.__remixContext = {')
        pos2 = page.find('};</script>', pos1)
        if -1 in [pos1, pos2]:
            return None
        bourne = self.json_loads(page[pos1 + 24:pos2 + 1].replace("'", '"').replace(':undefined', ':null'))
        chessgame = self.json_field(bourne, 'state/loaderData')
        chessgame = self.json_field(chessgame, 'routes/__app/games/$gameId', separator='|')

        # Rebuild the PGN game
        game = {}
        game['_url'] = url
        variant = self.json_field(chessgame, 'meta/variant')
        game['Event'] = 'Immortal game' if variant == 'immortal' else 'Standard game'
        game['Date'] = self.json_field(chessgame, 'state/updated/created_at')[:10]
        game['White'] = self.json_field(chessgame, 'meta/w/user/username')
        game['WhiteElo'] = self.json_field(chessgame, 'meta/w/user/elo')
        game['Black'] = self.json_field(chessgame, 'meta/b/user/username')
        game['BlackElo'] = self.json_field(chessgame, 'meta/b/user/elo')
        game['TimeControl'] = '%d+%d' % (self.json_field(chessgame, 'meta/limit'),
                                         self.json_field(chessgame, 'meta/increment'))
        if not self.json_field(chessgame, 'state/updated/is_finished'):
            game['Result'] = '*'
        else:
            winner = self.json_field(chessgame, 'state/updated/winner_color')
            if winner == 'w':
                game['Result'] = '1-0'
            elif winner == 'b':
                game['Result'] = '0-1'
            else:
                game['Result'] = '1/2-1/2'

        # Moves and clock
        game['_moves'] = ''
        moves = self.json_field(chessgame, 'state/updated/moves')
        if len(moves) == 0:
            game['_moves'] = ' '
        else:
            board = chess.Board()
            game['PlyCount'] = str(len(moves))
            for move in moves:
                try:
                    kmove = chess.Move.from_uci(move['from'] + move['to'] + move.get('promotion', ''))
                    game['_moves'] += ' ' + board.san(kmove)
                    board.push(kmove)
                except Exception:
                    return None

                # Clock
                clock = move['clock']['w' if board.turn == chess.BLACK else 'b'] / 1000.
                hour = clock // 3600
                clock -= hour * 3600
                minute = clock // 60
                clock -= minute * 60
                second = floor(clock)
                game['_moves'] += ' {[%%clk %d:%.2d:%.2d]}' % (hour, minute, second)
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://immortal.game/games/6299850f-ecb6-42dc-8d73-c3ed9b167332', True),     # Game with mate and promotion
                ('https://immortal.game/games/bc94f8bd-73eb-4681-b16b-eda56094fd31', True),     # Immortal game with timeout
                ('https://immortal.game/games/12345678-1234-1234-1234-123456789012', False),    # Not a game (wrong id)
                ('https://immortal.game', False),                                               # Not a game (home page)
                ]
