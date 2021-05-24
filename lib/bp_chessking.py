# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# ChessKing.com
class InternetGameChessking(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?chessking\.com\/games\/(ff\/)?([0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessKing.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(3))
            if gid.isdigit() and gid != '0' and len(gid) <= 9:
                if m.group(2) == 'ff/':
                    self.url_type = 'f'
                else:
                    self.url_type = 'g'
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Check
        if None in [self.url_type, self.id]:
            return None

        # Download
        id = self.id
        while len(id) < 9:
            id = '0%s' % id
        url = 'https://c1.chessking.com/pgn/%s/%s/%s/%s%s.pgn' % (self.url_type, id[:3], id[3:6], self.url_type, id)
        return self.download(url)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        # The direct PGN links are returned as 'application/octet-stream'
        return [('https://play.chessking.COM/games/4318271', True),             # Game of type G
                ('https://CHESSKING.com/games/ff/9859108', True),               # Game of type F
                ('https://play.chessking.com/games/1234567890', False),         # Not a game (ID too long)
                ('https://play.chessking.com', False)]                          # Not a game (homepage)
