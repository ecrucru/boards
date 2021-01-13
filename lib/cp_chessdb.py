# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_HTML
from lib.cp_interface import InternetGameInterface

import re
from urllib.parse import urlparse, parse_qs
from html.parser import HTMLParser


# Chess-DB.com
class InternetGameChessdb(InternetGameInterface):
    def get_identity(self):
        return 'Chess-DB.com', CAT_HTML

    def is_enabled(self):
        return False  # Server down

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.chess-db.com', 'chess-db.com'] or 'game.jsp' not in parsed.path.lower():
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'id' in args:
            gid = args['id'][0]
            rxp = re.compile(r'^[0-9\.]+$', re.IGNORECASE)
            if rxp.match(gid) is not None:
                self.id = gid
                return True
        return False

    def download_game(self):
        # Download
        if self.id is None:
            return None
        page = self.download('https://chess-db.com/public/game.jsp?id=%s' % self.id)
        if page is None:
            return None

        # Definition of the parser
        class chessdbparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.tag_ok = False
                self.pgn = None
                self.pgn_tmp = None

            def handle_starttag(self, tag, attrs):
                if tag.lower() == 'input':
                    for k, v in attrs:
                        k = k.lower()
                        if k == 'name' and v == 'pgn':
                            self.tag_ok = True
                        if k == 'value' and v.count('[') == v.count(']'):
                            self.pgn_tmp = v

            def handle_data(self, data):
                if self.pgn is None and self.tag_ok:
                    self.pgn = self.pgn_tmp

        # Read the PGN
        parser = chessdbparser()
        parser.feed(page)
        return parser.pgn

    def get_test_links(self):
        return [('https://CHESS-DB.COM/public/game.jsp?id=623539.1039784.81308416.30442', True),        # Game
                ('https://chess-db.com/public/game.jsp?id=623539.2900084.7718912.30537', False),        # Game but website bug with escaping '
                ('https://chess-db.com/public/game.jsp?id=123456.1234567.1234567.123456789', False),    # Not a game (unknown game)
                ('https://chess-db.com/public/game.jsp?id=ABC123', False),                              # Not a game (wrong ID)
                ('https://chess-db.com/play.jsp?id=623539.1039784.81308416.30442', False),              # Not a game (wrong path)
                ('https://chess-db.com', False)]                                                        # Not a game (homepage)
