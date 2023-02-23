# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# LiveChess24.com
class InternetGameLivechess24(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/livechess24\.com\/Tournaments\/(\w+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'LiveChess24.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = m.group(1)
            return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is None:
            return None
        return self.download('http://livechess24.com/downloadPgn?tourn=%s' % self.id)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://livechess24.com/Tournaments/V_stg_ta_Open_2023?round=6', True),                            # Tournament
                ('http://livechess24.com/Tournaments/Elite_Hotels_Open_2023?round=8&singleViewMode=true', True),    # Game (detailed view)
                ('http://livechess24.com/Tournaments/Elite_Hotels_Open_2012', False),                               # Not a game (wrong tournament)
                ('http://livechess24.com/downloadPgn?tourn=Elite_Hotels_Open_2023', False),                         # Not a game (direct link)
                ('http://livechess24.com', False),                                                                  # Not a game (homepage)
                ]
