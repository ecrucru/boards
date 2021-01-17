# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# Dragongoserver.net
class InternetGameDragongoserver(InternetGameInterface):
    def get_identity(self):
        return 'DragonGoServer.net', BOARD_GO, METHOD_DL

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() in ['www.dragongoserver.net', 'dragongoserver.net']:
            # Read the arguments
            args = parse_qs(parsed.query)
            if 'gid' in args:
                gid = args['gid'][0]
                if gid.isdigit() and gid != '0':
                    self.id = gid
                    return True
        return False

    def download_game(self):
        if self.id is not None:
            return self.download('https://www.dragongoserver.net/sgf.php?gid=%s' % self.id)
        else:
            return None

    def get_test_links(self):
        return [('http://www.dragongoserver.net/game.php?gid=1347414#tag', True),       # Game
                ('https://www.dragongoserver.net/sgf.php?gid=1347414&arg', True),       # Download link
                ('http://www.DRAGONGOSERVER.net/gameinfo.php?gid=1347414', True),       # Game info
                ('https://www.dragongoserver.NET/manage_sgf.php?gid=1347414', True),    # Manage game
                ('https://www.dragongoserver.net/fakepage.php?gid=1347414#tag', True),  # Non-existing page but the gid matters
                ('https://www.dragongoserver.net/game.php?gid=999999999', False),       # Not a game (unknown ID)
                ('https://www.dragongoserver.net/game.php?gid=hello', False),           # Not a game (invalid ID)
                ('https://www.dragongoserver.net', False)]                              # Not a game (homepage)
