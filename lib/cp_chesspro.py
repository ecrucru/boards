# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_HTML
from lib.cp_interface import InternetGameInterface

import re


# ChessPro.ru
class InternetGameChesspro(InternetGameInterface):
    def get_identity(self):
        return 'ChessPro.ru', CAT_HTML

    def assign_game(self, url):
        return self.reacts_to(url, 'chesspro.ru')

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Download the page
        page = self.download(self.id)
        if page is None:
            return None

        # Find the chess widget
        rxp = re.compile(r'.*OpenGame\(\s*"g[0-9]+\"\s*,"(.*)"\s*\)\s*;.*', re.IGNORECASE)
        lines = page.split("\n")
        for line in lines:
            m = rxp.match(line)
            if m is not None:
                return '[Annotator "ChessPro.ru"]\n%s' % m.group(1)
        return None

    def get_test_links(self):
        return [('https://chessPRO.ru/details/grand_prix_moscow19_day8', True),         # Article with game and no header
                ('https://chesspro.ru/details/grand_prix_moscow19_day11', False),       # Article without game
                ('https://chesspro.ru', False)]                                         # Not a game (homepage)
