# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface


# Ficgs.com
class InternetGameFicgs(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?ficgs\.com\/game_(\d+).html', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Ficgs.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Download
        return self.download('http://www.ficgs.com/game_%s.pgn' % self.id)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://FICGS.com/game_95671.html', True),             # Game
                ('http://www.ficgs.com/game_1234567890.html', False),   # Not a game (wrong ID)
                ('http://www.ficgs.com/view_95671.html', False),        # Not a game (wrong path)
                ('http://www.ficgs.com', False)]                        # Not a game (homepage)
