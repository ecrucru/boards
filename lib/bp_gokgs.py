# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface

import re


# GoKGS.com
class InternetGameGokgs(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^(https?:\/\/files\.gokgs\.com\/games\/[0-9]+\/[0-9]+\/[0-9]+\/[^\/]+\.sgf)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self):
        return 'GoKGS.com', BOARD_GO, METHOD_DL

    def assign_game(self, url):
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = m.group(1)
            return True
        return False

    def download_game(self):
        return self.download(self.id)

    def get_test_links(self):
        return [('http://files.gokgs.com/games/2020/3/23/patrickb-yasusaka.sgf', True),     # Game
                ('http://files.gokgs.com/games/2019/10/20/mutaku-hellsflame.sgf', True),    # Game from tournament
                ('http://files.gokgs.com/games/1970/01/01/incorrect.sgf', False),           # Not a game (unknown game)
                ('http://www.gokgs.com', False)]                                            # Not a game (homepage)
