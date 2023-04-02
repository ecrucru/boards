# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from urllib.parse import urlparse

from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface


# ChessBomb.com (merged into Chess.com)
class InternetGameChessbomb(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessBomb.com', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc in ['chess.com', 'www.chess.com', 'nxt.chessbomb.com']:
            gid = parsed.path.replace('/api/game/', '/')
            if gid[:8] == '/events/':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Get the JSON
        if self.id is None:
            return None
        url = 'https://nxt.chessbomb.com/events/api/game/%s' % self.id[8:]
        bourne = self.send_xhr(url, {})     # {} = POST
        if bourne is None:
            return None
        data = self.json_loads(bourne)

        # Interpret the JSON
        game = {}
        game['_url'] = 'https://www.chess.com' + self.id
        game['Event'] = self.json_field(data, 'room/name')
        game['Site'] = self.json_field(data, 'room/officialUrl')
        game['Date'] = self.json_field(data, 'game/startAt')[:10]
        game['Round'] = '%s.%s' % (self.json_field(data, 'game/table', '?'),
                                   self.json_field(data, 'game/board', '?'))
        game['White'] = self.json_field(data, 'game/white/name')
        game['WhiteElo'] = self.json_field(data, 'game/white/elo')
        game['WhiteTitle'] = self.json_field(data, 'game/white/title')
        game['Black'] = self.json_field(data, 'game/black/name')
        game['BlackElo'] = self.json_field(data, 'game/black/elo')
        game['BlackTitle'] = self.json_field(data, 'game/black/title')
        game['Result'] = self.json_field(data, 'game/result')

        game['_moves'] = ''
        for move in self.json_field(data, 'moves'):
            # Move
            smove = self.json_field(move, 'cbn')
            pos = smove.find('_')
            if pos != -1:
                smove = smove[pos + 1:]
            game['_moves'] += '%s ' % smove

            # Clock
            clock = self.json_field(move, 'clock')
            if clock != '':
                game['_moves'] += '{[%%clk %02d:%02d:%02d]} ' % self.seconds2clock(round(clock / 1000))

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://nxt.chessbomb.com/events/2022-2023-4ncl-division-1/01/Bobras_Piotr-Wall_Gavin', True),            # Game
                ('https://www.chess.com/events/2019-katowice-chess-festival-im/04/Kubicka_Anna-Sliwicka_Alicja', True),     # Game
                ('https://www.chess.com/events/2018-catalan-chess-team-league', True),                                      # Not a game (wrong id)
                ('https://nxt.chessbomb.com/page/about/01/nothing', False)                                                  # Not a game (wrong path)
                ]
