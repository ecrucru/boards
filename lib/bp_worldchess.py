# Copyright (C) 2025 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface


# WorldChess.com
class InternetGameWorldchess(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?worldchess\.com\/game\/([0-9a-f-]{36})[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'WorldChess.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = str(m.group(2))
            return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            return self.download(f'https://api.worldchess.com/api/online/gaming/{self.id}/pgn/')
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://worldchess.com/game/3515cc6c-4d69-482d-9246-9662eb656bae', True),     # Game
                ('https://worldchess.com/game/12345678-90ab-cdef-1234-567890abcdef', False),    # Not a game (wrong id)
                ('https://worldchess.com', False)]                                              # Not a game (homepage)
