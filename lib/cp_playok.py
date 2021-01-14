# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_DL
from lib.cp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# PlayOK.com
class InternetGamePlayok(InternetGameInterface):
    def get_identity(self):
        return 'PlayOK.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url):
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.playok.com', 'playok.com']:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'g' in args:
            gid = args['g'][0]
            if gid[:2] == 'ch':
                gid = gid[2:].replace('.txt', '')
                if gid.isdigit() and gid != '0':
                    self.id = gid
                    return True
        return False

    def download_game(self):
        if self.id is not None:
            pgn = self.download('https://www.playok.com/p/?g=ch%s.txt' % self.id)
            if len(pgn) > 16:
                return pgn
        return None

    def get_test_links(self):
        return [('http://www.playok.com/p/?g=ch484680868', True),       # Game
                ('https://PLAYOK.com/p/?g=ch484680868.txt', True),      # Game (direct link)
                ('https://PLAYOK.com/p/?g=ch999999999#tag', False),     # Game (wrong ID)
                ('http://www.playok.com', False)]                       # Not a game (homepage)
