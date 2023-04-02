# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from html.parser import HTMLParser

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# ChessPuzzle.net
class InternetGameChesspuzzle(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?chesspuzzle\.net\/(Puzzle|Solution)\/([0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessPuzzle.net', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(3))
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Download the puzzle
        page = self.download('https://chesspuzzle.net/Solution/%s' % self.id)
        if page is None:
            return None

        # Definition of the parser
        class chesspuzzleparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.last_tag = None
                self.pgn = None

            def handle_starttag(self, tag, attrs):
                self.last_tag = tag.lower()

            def handle_data(self, data):
                if self.pgn is None and self.last_tag == 'script':
                    pos1 = data.find('ChessViewer(')
                    if pos1 != -1:
                        pos1 = data.find("'", pos1 + 1)
                        pos2 = data.find("'", pos1 + 1)
                        if pos1 != -1 and pos2 > pos1:
                            self.pgn = data[pos1 + 1:pos2].replace(']  ', "]\n\n").replace('] ', "]\n").strip()

        # Get the puzzle
        parser = chesspuzzleparser()
        parser.feed(page)
        return parser.pgn

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chesspuzzle.net/Puzzle/23476', True),                 # Puzzle from the quiz
                ('https://CHESSPUZZLE.net/Solution/32881', True),               # Puzzle from the solution
                ('https://chesspuzzle.net/Puzzle', False),                      # Not a puzzle (random link)
                ('https://chesspuzzle.net/Puzzle/123456789', False),            # Not a puzzle (wrong ID)
                ('https://chesspuzzle.net', False)]                             # Not a puzzle (homepage)
