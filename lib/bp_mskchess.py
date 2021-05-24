# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# MskChess.ru
class InternetGameMskchess(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'game': re.compile(r'^https?:\/\/mskchess\.ru\/(game\/export\/|embed\/)?([a-z0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'MskChess.ru', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['game'].match(url)
        if m is not None:
            gid = m.group(2)
            if len(gid) == 8:
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Minimalist support for the clones of Lichess
        if self.id is not None:
            return self.download('https://mskchess.ru/game/export/%s?literate=1' % self.id)
        else:
            return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://mskchess.ru/jvcVna2g?arg', True),         # Game
                ('https://MSKCHESS.ru/jvcVna2g/black#tag', True),   # Game (from black side)
                ('https://mskchess.ru/123Vna2Z/black', False),      # Not a game (invalid ID)
                ('https://mskchess.ru', False)]                     # Not a game (homepage)
