# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# Europe-Echecs.com
class InternetGameEuropeechecs(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'widget': re.compile(r".*class=\"cbwidget lazy\"\s+id=\"([0-9a-f]+)_container\".*", re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Europe-Echecs.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, 'europe-echecs.com')

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Find the links
        links = []
        if self.id.lower().endswith('.pgn'):
            links.append(self.id)
        else:
            # Download the page
            page = self.download(self.id)
            if page is None:
                return None

            # Find the chess widgets
            lines = page.split("\n")
            for line in lines:
                m = self.regexes['widget'].match(line)
                if m is not None:
                    links.append('https://www.europe-echecs.com/embed/doc_%s.pgn' % m.group(1))

        # Collect the games
        return self.download_list(links)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.europe-echecs.com/art/championnat-d-europe-f-minin-2019-7822.html', True),    # Embedded games
                ('https://www.EUROPE-ECHECS.com/embed/doc_a2d179a4a201406d4ce6138b0b1c86d7.pgn', True),     # Direct link
                ('https://www.europe-echecs.com', False)]                                                   # Not a game (homepage)
