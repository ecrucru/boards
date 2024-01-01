# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2024 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from urllib.parse import urlparse, parse_qs

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# 2700chess.com
class InternetGame2700chess(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return '2700chess.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.2700chess.com', '2700chess.com']:
            return False

        # Refactor the direct link
        if parsed.path.lower() == '/games/download':
            args = parse_qs(parsed.query)
            if 'slug' in args:
                self.id = 'https://2700chess.com/games/%s' % args['slug'][0]
                return True

        # Verify the path
        if parsed.path.startswith('/games/'):
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

        # Extract the PGN
        p1 = page.find('pgn: `')
        p2 = page.find('`,', p1)
        if -1 < p1 < p2:
            return page[p1 + 6:p2].strip()
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://2700CHESS.com/games/dominguez-perez-yu-yangyi-r19.6-hengshui-chn-2019-05-18', True),                      # Game
                ('https://2700chess.com/games/download?slug=dominguez-perez-yu-yangyi-r19.6-hengshui-chn-2019-05-18#tag', True),    # Game with direct link
                ('https://2700chess.COM/games/pychess-r1.1-paris-fra-2019-12-25', False),                                           # Not a game (wrong ID)
                ('https://2700chess.com', False)]                                                                                   # Not a game (homepage)
