# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface


# Chess-Samara.ru
class InternetGameChesssamara(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?chess-samara\.ru\/(\d+)\-', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Chess-Samara.ru', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and (gid != '0'):
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            return self.download('https://chess-samara.ru/view/pgn.html?gameid=%s' % self.id)
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chess-SAMARA.ru/68373335-igra-Firudin1888-vs-Pizyk', True),       # Game
                ('https://chess-samara.ru/view/pgn.html?gameid=68373335', False),           # Game in direct link but handled by the generic extractor
                ('https://chess-samara.ru/1234567890123-pychess-vs-pychess', False),        # Not a game (wrong ID)
                ('https://chess-samara.ru', False)]                                         # Not a game (homepage)
