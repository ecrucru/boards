# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_DL
from lib.cp_interface import InternetGameInterface

import re


# Chess-Samara.ru
class InternetGameChesssamara(InternetGameInterface):
    def get_identity(self):
        return 'Chess-Samara.ru', CAT_DL

    def assign_game(self, url):
        rxp = re.compile(r'^https?:\/\/(\S+\.)?chess-samara\.ru\/(\d+)\-', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Download
        pgn = self.download('https://chess-samara.ru/view/pgn.html?gameid=%s' % self.id)
        if pgn is None or len(pgn) == 0:
            return None
        else:
            return pgn

    def get_test_links(self):
        return [('https://chess-SAMARA.ru/68373335-igra-Firudin1888-vs-Pizyk', True),       # Game
                ('https://chess-samara.ru/view/pgn.html?gameid=68373335', False),           # Game in direct link but handled by the generic extractor
                ('https://chess-samara.ru/1234567890123-pychess-vs-pychess', False),        # Not a game (wrong ID)
                ('https://chess-samara.ru', False)]                                         # Not a game (homepage)
