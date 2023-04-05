# Copyright (C) 2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from math import floor

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
            elif winner == game['Black']:
                game['Result'] = '0-1'
            else:
                game['Result'] = '1/2-1/2'

        # Moves and clock
        game['_moves'] = ''
        moves = self.json_field(chessgame, 'state/updated/moves')
        if len(moves) == 0:
            game['_moves'] = ' '
        else:
            game['PlyCount'] = len(moves)
            for move in moves:
                game['_moves'] += ' ' + move['san']

                # Clock
                clock = move['clock'][move['color']] / 1000.
                hour = clock // 3600
                clock -= hour * 3600
                minute = clock // 60
                clock -= minute * 60
                second = floor(clock)
                game['_moves'] += ' {[%%clk %d:%.2d:%.2d]}' % (hour, minute, second)
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://immortal.game/games/fd73b68c-a3d0-4dd7-9530-8e74d1bb52ea', True),     # Game with mate
                ('https://immortal.game/games/18c2c3a0-e24f-4c2a-aaab-1a7ef12b8968', True),     # Game with timeout
                ('https://immortal.game/games/244e891b-4a37-46f9-9474-f4f17e741b40', True),     # Game without move
                ('https://immortal.game/games/6c3af1d6-61f0-45c8-a93f-b0d74be48aeb', True),     # Immortal game
                ('https://immortal.game/games/a4c23fb2-7b4b-4a71-bdbf-63578dff0bba', True),     # Immortal game with cyrillic name
                ('https://immortal.game/games/4e135f9a-7f57-43e5-bc32-03564e04a218', True),     # Immortal game with draw
                ('https://immortal.game', False),                                               # Not a game (home page)
                ]
