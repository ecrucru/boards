# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface


# Online-go.com
class InternetGameOnlinego(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/online-go\.com\/(api\/v1\/)?games?\/([0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Online-go.com', BOARD_GO, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = m.group(2)
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            return self.download('https://online-go.com/api/v1/games/%s/sgf' % self.id)
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://online-go.com/game/30113933#tag', True),               # Game
                ('http://online-go.com/game/999930113933#tag', False),          # Not a game (invalid id)
                ('https://ONLINE-GO.com/api/v1/games/30113933/sgf', True),      # Game (direct link)
                ('https://online-go.com/api/v1/games/30113933/sgf?ai_review=0b0e875a-b3a3-4a3c-847c-a7474e50d6c5', True),   # Game (direct link with ignored analysis id)
                ('https://online-go.com', False)]                               # Not a game (homepage)
