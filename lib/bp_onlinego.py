# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# Online-go.com
class InternetGameOnlinego(InternetGameInterface):
    def get_identity(self):
        return 'Online-go.com', BOARD_GO, METHOD_DL

    def assign_game(self, url):
        m = re.compile(r'^https?:\/\/online-go\.com\/(api\/v1\/)?games?\/([0-9]+)[\/\?\#]?', re.IGNORECASE).match(url)
        if m is not None:
            gid = m.group(2)
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self):
        if self.id is not None:
            return self.download('https://online-go.com/api/v1/games/%s/sgf' % self.id, userAgent=True)
        else:
            return None

    def get_test_links(self):
        return [('http://online-go.com/game/30113933#tag', True),               # Game
                ('http://online-go.com/game/999930113933#tag', False),          # Not a game (invalid id)
                ('https://ONLINE-GO.com/api/v1/games/30113933/sgf', True),      # Game (direct link)
                ('https://online-go.com/api/v1/games/30113933/sgf?ai_review=0b0e875a-b3a3-4a3c-847c-a7474e50d6c5', True),   # Game (direct link with ignored analysis id)
                ('https://online-go.com', False)]                               # Not a game (homepage)
