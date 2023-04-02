# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from urllib.parse import urlparse, parse_qs

from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface


# GChess.com
class InternetGameGchess(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'GChess.com', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        # Verify the host
        parsed = urlparse(url.replace('/#/', '/'))
        if parsed.netloc.lower() not in ['www.gchess.com', 'gchess.com']:
            return False

        # Read the identifier
        args = parse_qs(parsed.query)
        if 'game' in args:
            gid = args['game'][0].replace('top-games-', '')
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is None:
            return None
        url = 'https://gchess.com/api/game.php?id=%s' % self.id
        bourne = self.send_xhr(url, None)
        data = self.json_loads(bourne)
        if data is None:
            return None
        pgn = data.get('pgn', '').replace('\r', '')
        return re.sub(r'(?<!")\]\n', '"]\n', pgn)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://gchess.com/#/games/top-games?game=top-games-9961486&orientation=white', True),    # Game
                ('https://gchess.com/dummy?game=top-games-566682', True),                                   # Game
                ('https://gchess.com/dummy?id=566682', False),                                              # Not a game (wrong parameter)
                ('https://gchess.com', False),                                                              # Not a game (homepage)
                ]
