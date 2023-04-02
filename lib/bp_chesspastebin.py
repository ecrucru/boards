# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from html.parser import HTMLParser

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# ChessPastebin.com
class InternetGameChesspastebin(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'widget': re.compile(r'.*?\<div id=\"([0-9]+)_board\"\>\<\/div\>.*?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessPastebin.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, 'chesspastebin.com')

    def download_game(self) -> Optional[str]:
        # Download
        if self.id is None:
            return None
        page = self.download(self.id)
        if page is None:
            return None

        # Extract the game ID
        m = self.regexes['widget'].match(page.replace("\n", ''))
        if m is None:
            return None
        gid = m.group(1)

        # Definition of the parser
        class chesspastebinparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.tag_ok = False
                self.pgn = None

            def handle_starttag(self, tag, attrs):
                if tag.lower() == 'div':
                    for k, v in attrs:
                        if k.lower() == 'id' and v == gid:
                            self.tag_ok = True

            def handle_data(self, data):
                if self.pgn is None and self.tag_ok:
                    self.pgn = data

        # Read the PGN
        parser = chesspastebinparser()
        parser.feed(page)
        pgn = parser.pgn
        if pgn is not None:  # Any game must start with '[' to be considered further as valid
            pgn = pgn.strip()
            if not pgn.startswith('['):
                pgn = "[Annotator \"ChessPastebin.com\"]\n%s" % pgn
        return pgn

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.chesspastebin.com/2018/12/29/anonymous-anonymous-by-george-2/', True),        # Game quite complete
                ('https://www.CHESSPASTEBIN.com/2019/04/14/unknown-unknown-by-alekhine-sapladi/', True),    # Game with no header
                ('https://www.chesspastebin.com/1515/09/13/marignan/', False),                              # Not a game (invalid URL)
                ('https://www.chesspastebin.com', True)]                                                    # Game from homepage
