# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_DL, TYPE_EVENT, TYPE_GAME
from lib.cp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# Iccf.com
class InternetGameIccf(InternetGameInterface):
    def get_identity(self):
        return 'Iccf.com', CAT_DL

    def assign_game(self, url):
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.iccf.com', 'iccf.com']:
            return False

        # Verify the path
        ppl = parsed.path.lower()
        if '/game' in ppl:
            ttyp = TYPE_GAME
        elif '/event' in ppl:
            ttyp = TYPE_EVENT
        else:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'id' in args:
            gid = args['id'][0]
            if gid.isdigit() and gid != '0':
                self.url_type = ttyp
                self.id = gid
                return True
        return False

    def download_game(self):
        # Check
        if self.url_type not in [TYPE_GAME, TYPE_EVENT] or self.id is None:
            return None

        # Download
        if self.url_type == TYPE_GAME:
            url = 'https://www.iccf.com/GetPGN.aspx?id=%s'
        elif self.url_type == TYPE_EVENT:
            url = 'https://www.iccf.com/GetEventPGN.aspx?id=%s'
        pgn = self.download(url % self.id)
        if pgn in [None, ''] or 'does not exist.' in pgn or 'Invalid event' in pgn:
            return None
        else:
            return pgn

    def get_test_links(self):
        return [('https://www.iccf.COM/game?id=154976&param=foobar', True),     # Game
                ('https://www.iccf.com/GetPGN.aspx?id=154976', False),          # Game in direct link but handled by the generic extractor
                ('https://www.iccf.com/game?id=abc123', False),                 # Not a game (wrong ID)
                ('https://www.iccf.com/officials?id=154976', False),            # Not a game (invalid path)
                ('https://www.iccf.com', False),                                # Not a game (homepage)
                ('https://ICCF.com/event?id=13581#tag', True),                  # Event
                ('https://www.iccf.com/GetEventPGN.aspx?id=13581', False),      # Event in direct link but handled by the generic extractor
                ('https://www.iccf.com/event?id=abc123', False)]                # Not an event (wrong ID)
