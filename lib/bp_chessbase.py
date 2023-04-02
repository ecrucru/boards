# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from html.parser import HTMLParser

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# Chessbase
class InternetGameChessbase(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessBase.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, '*')             # Any website can embed a widget from Chessbase

    def download_game(self) -> Optional[str]:
        # Download
        if self.id is None:
            return None
        page = self.download(self.id)
        if page is None:
            return None

        # Definition of the parser
        class chessbaseparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.tag_ok = False
                self.links = []
                self.pgn = None

            def handle_starttag(self, tag, attrs):
                # Verify the parent tag
                self.tag_ok = False
                if tag.lower() in ['p', 'div']:
                    for k, v in attrs:
                        if k.lower() == 'class' and v == 'cbreplay':
                            self.tag_ok = True

                    # Content by link
                    if self.tag_ok:
                        for k, v in attrs:
                            if k.lower() == 'data-url':
                                self.links.append(v)

            def handle_data(self, data):
                # Content by data
                if self.tag_ok and self.pgn is None:
                    data = data.strip()
                    if len(data) > 0:       # Empty content if data-url used
                        self.pgn = data

        # Parse the page
        parser = chessbaseparser()
        parser.feed(page)
        if parser.pgn is not None:
            return parser.pgn
        parser.links = self.expand_links(parser.links, self.id)
        return self.download_list(parser.links)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://live.chessbase.com/fr/Games?id=lcc-england-vs-row-2021', True),                               # Games
                ('https://live.chessbase.com/fr/Replay?id=lcc-england-vs-row-2021&rnd=3&anno=False', True),             # Games with parameters
                ('https://live.chessbase.com/fr/Watch?id=lcc-england-vs-row-2021', False),                              # Not a game (old link)
                ('https://liveserver.chessbase.com:6009/pgn/5th-eka-iifl-investment-2019/all.pgn#fake-tag', False),     # Not a game (direct PGN link)
                ('https://live.chessbase.com', False)]                                                                  # Not a game (homepage)
