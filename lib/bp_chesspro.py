# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# ChessPro.ru
class InternetGameChesspro(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'widget': re.compile(r'.*OpenGame\(\s*"g[0-9]+\"\s*,"(.*)"\s*\)\s*;.*', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessPro.ru', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, 'chesspro.ru')

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Download the page
        page = self.download(self.id)
        if page is None:
            return None

        # Find the chess widget
        lines = page.split("\n")
        for line in lines:
            m = self.regexes['widget'].match(line)
            if m is not None:
                return '[Annotator "ChessPro.ru"]\n%s' % m.group(1)
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chessPRO.ru/details/grand_prix_moscow19_day8', True),         # Article with game and no header
                ('https://chesspro.ru/details/grand_prix_moscow19_day11', False),       # Article without game
                ('https://chesspro.ru', False)]                                         # Not a game (homepage)
