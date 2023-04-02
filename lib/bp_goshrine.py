# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface


# GoShrine.com
class InternetGameGoshrine(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/goshrine\.com\/g\/([a-z0-9]{8})[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'GoShrine.com', BOARD_GO, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = m.group(1)
            return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            data = self.download('http://goshrine.com/g/%s.sgf' % self.id)
            if data != 'Game not found!':
                return data
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://goshrine.com/g/f8a82242', True),       # Game
                ('http://goshrine.com/g/f8a82242#tag', True),   # Game
                ('http://goshrine.com/g/f8a82242?arg', True),   # Game
                ('http://goshrine.com/g/aabbccdd', False),      # Not a game (invalid ID)
                ('http://goshrine.com', False)]                 # Not a game (homepage)
