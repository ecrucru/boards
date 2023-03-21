# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re
from urllib.parse import urlparse


# ChessArena.com
class InternetGameChessarena(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes['id'] = re.compile(r'([0-9a-f-]{36})', re.IGNORECASE)

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessArena.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.chessarena.com', 'chessarena.com']:
            return False

        # Verify the identifier
        m = self.regexes['id'].search(url)
        if m is not None:
            self.id = m.group(1)
            return True
        else:
            return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            return self.download('https://api.worldchess.com/api/online/gaming/%s/pgn/' % self.id)
        else:
            return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chessarena.com/v2/tournament_game/17fb7e7f-24e0-4b71-8d7a-8a0fc7b7fa6c', True),   # Game
                ('https://chessarena.com/v2/tournament_game/4c98cdf3-cae4-4ceb-b117-723b2ef2572e', False),  # Not a game (wrong id)
                ('https://chessarena.com', False)]                                                          # Not a game (homepage)
