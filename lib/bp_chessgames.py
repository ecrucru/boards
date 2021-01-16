# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# ChessGames.com
class InternetGameChessgames(InternetGameInterface):
    def reset(self):
        InternetGameInterface.reset(self)
        self.computer = False

    def get_identity(self):
        return 'ChessGames.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url):
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.chessgames.com', 'chessgames.com']:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'gid' in args:
            gid = args['gid'][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.computer = ('comp' in args) and (args['comp'][0] == '1')
                return True
        return False

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # First try with computer analysis
        url = 'http://www.chessgames.com/pgn/chessdl.pgn?gid=' + self.id
        if self.computer:
            pgn = self.download(url + '&comp=1')
            if pgn in [None, ''] or 'NO SUCH GAME' in pgn:
                self.computer = False
            else:
                return pgn

        # Second try without computer analysis
        if not self.computer:
            pgn = self.download(url)
            if pgn in [None, ''] or 'NO SUCH GAME' in pgn:
                return None
            else:
                return pgn

    def get_test_links(self):
        return [('http://www.chessgames.com/perl/chessgame?gid=1075462&comp=1', True),              # With computer analysis
                ('http://www.chessgames.com/perl/chessgame?gid=1075463', True),                     # Without computer analysis
                ('http://www.CHESSGAMES.com/perl/chessgame?gid=1075463&comp=1#test', True),         # Without computer analysis but requested in URL
                ('http://www.chessgames.com/perl/chessgame?gid=1234567890', False)]                 # Not a game
