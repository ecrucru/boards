# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface


# Echecs-Online.eu
class InternetGameEchecsonline(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/www.echecs-online\.eu\/(game|analyse)\/([a-z0-9]{8})[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Echecs-Online.eu', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = m.group(2)
            return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is None:
            return None
        data = self.download('https://www.echecs-online.eu/analyse/%s' % self.id)
        p1 = data.find('<textarea id="pgnText"')
        p2 = data.find('</textarea>', p1)
        if -1 not in [p1, p2]:
            p1 = data.find('>', p1)
            if p2 > p1:
                return data[p1 + 1:p2]
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.echecs-online.eu/game/07af79f4', True),               # Game
                ('https://www.echecs-online.eu/analyse/07af79f4', True),            # Game (analysis)
                ('https://www.echecs-online.eu/game/07af79f4/black', True),         # Game (from black side)
                ('https://www.echecs-online.eu/game/07af79f4/stats', True),         # Game (statistics)
                ('http://www.echecs-online.eu', False)]                             # Not a game (homepage)
