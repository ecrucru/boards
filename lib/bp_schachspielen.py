# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_HTML, CHESS960
from lib.bp_interface import InternetGameInterface

import re
from html.parser import HTMLParser


# Schach-Spielen.eu
class InternetGameSchachspielen(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(www\.)?schach-spielen\.eu\/(game|analyse)\/([a-z0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Schach-Spielen.eu', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) == 8:
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Download
        if self.id is None:
            return None
        page = self.download('https://www.schach-spielen.eu/analyse/%s' % self.id)
        if page is None:
            return None

        # Definition of the parser
        class schachspielenparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.tag_ok = False
                self.pgn = None

            def handle_starttag(self, tag, attrs):
                if tag.lower() == 'textarea':
                    for k, v in attrs:
                        if k.lower() == 'id' and v == 'pgnText':
                            self.tag_ok = True

            def handle_data(self, data):
                if self.pgn is None and self.tag_ok:
                    self.pgn = data

        # Read the PGN
        parser = schachspielenparser()
        parser.feed(page)
        pgn = parser.pgn
        if pgn is not None:
            pgn = pgn.replace('[Variant "chess960"]', '[Variant "%s"]' % CHESS960)
        return pgn

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.schach-spielen.eu/analyse/2jcpl1vs/black#test', True),       # Best game ever with anchor
                ('http://schach-SPIELEN.eu/game/2jcpl1vs?p=1', True),                      # Best game ever with parameter
                ('https://www.schach-spielen.eu/game/8kcevvdy/white', True),               # Chess960
                ('https://www.schach-spielen.eu/game/IENSUIEN', False),                    # Not a game (wrong ID)
                ('https://www.schach-spielen.eu/about/8kcevvdy', False),                   # Not a game (bad URL)
                ('https://www.schach-SPIELEN.eu', False)]                                  # Not a game (homepage)
