# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# TheChessWorld.com
class InternetGameThechessworld(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r".*pgn_uri:.*'([^']+)'.*", re.IGNORECASE)})

    def get_identity(self):
        return 'TheChessWorld.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url):
        return self.reacts_to(url, 'thechessworld.com')

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Find the links
        links = []
        if self.id.lower().endswith('.pgn'):
            links.append(self.id)
        else:
            # Download the page
            data = self.download(self.id)
            if data is None:
                return None

            # Finds the games
            lines = data.split("\n")
            for line in lines:
                m = self.regexes['url'].match(line)
                if m is not None:
                    links.append('https://www.thechessworld.com' + m.group(1))

        # Collect the games
        return self.download_list(links)

    def get_test_links(self):
        return [('https://thechessworld.com/articles/middle-game/typical-sacrifices-in-the-middlegame-sacrifice-on-e6/', True),     # 3 embedded games
                ('https://THECHESSWORLD.com/pgngames/middlegames/sacrifice-on-e6/Ivanchuk-Karjakin.pgn', True),                     # Direct link
                ('https://thechessworld.com/help/about/', False)]                                                                   # Not a game (about page)
