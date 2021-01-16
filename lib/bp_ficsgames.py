# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# FicsGames.org
class InternetGameFicsgames(InternetGameInterface):
    def get_identity(self):
        return 'FicsGames.org', BOARD_CHESS, METHOD_DL

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.ficsgames.org', 'ficsgames.org'] or 'show' not in parsed.path.lower():
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'ID' in args:
            gid = args['ID'][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Download
        pgn = self.download('http://ficsgames.org/cgi-bin/show.cgi?ID=%s;action=save' % self.id)
        if pgn in [None, ''] or 'not found in GGbID' in pgn:
            return None
        else:
            return pgn

    def get_test_links(self):
        return [('https://www.ficsgames.org/cgi-bin/show.cgi?ID=451813954;action=save', True),      # Normal game
                ('https://www.ficsgames.org/cgi-bin/show.cgi?ID=qwertz;action=save', False),        # Invalid identifier (not numeric)
                ('https://www.ficsgames.org/cgi-bin/show.cgi?ID=0#anchor', False),                  # Invalid identifier (null)
                ('https://www.ficsgames.org/about.html', False)]                                    # Not a game
