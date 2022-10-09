# Copyright (C) 2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface

import re
from math import floor


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
        chessgame = self.json_field(bourne, 'routeData|routes/games/$gameId', separator='|')

        # Rebuild the PGN game
        game = {}
        game['_url'] = url
        variant = self.json_field(chessgame, 'variant')
        game['Event'] = 'Immortal game' if variant == 'immortal' else 'Standard game'
        speed = self.json_field(chessgame, 'gameSpeed')
        game['White'] = self.json_field(chessgame, 'players/white/username')
        elo = self._str2int(self.json_field(chessgame, 'players/white/perfs/%s/%s/glicko/rating' % (variant, speed)))
        if elo > 0:
            game['WhiteElo'] = str(elo)
        game['Black'] = self.json_field(chessgame, 'players/black/username')
        elo = self._str2int(self.json_field(chessgame, 'players/black/perfs/%s/%s/glicko/rating' % (variant, speed)))
        if elo > 0:
            game['BlackElo'] = str(elo)
        tc = self.json_field(chessgame, 'playAgainConfig/speed').split('+')
        game['TimeControl'] = '%d+%s' % (int(tc[0]) * 60, tc[1])
        winner = self.json_field(chessgame, 'initialWinner/username')
        if winner == game['White']:
            game['Result'] = '1-0'
        elif winner == game['Black']:
            game['Result'] = '0-1'
        else:
            game['Result'] = '1/2-1/2'

        # Moves and clock
        game['_moves'] = ''
        moves = self.json_field(chessgame, 'initialHistory')
        if len(moves) == 0:
            game['_moves'] = ' '
        else:
            for move in moves:
                game['_moves'] += ' ' + move['san']
                game['PlyCount'] = move['ply']

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
