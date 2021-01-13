# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_HTML, TYPE_GAME, TYPE_PUZZLE
from lib.cp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs
from html.parser import HTMLParser


# RedHotPawn.com
class InternetGameRedhotpawn(InternetGameInterface):
    def get_identity(self):
        return 'RedHotPawn.com', CAT_HTML

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.redhotpawn.com', 'redhotpawn.com']:
            return False

        # Verify the path
        ppl = parsed.path.lower()
        if 'chess-game-' in ppl:
            ttype = TYPE_GAME
            key = 'gameid'
        elif 'chess-puzzle-' in ppl:
            ttype = TYPE_PUZZLE
            if 'chess-puzzle-serve' in url.lower():
                self.url_type = ttype
                self.id = url
                return True
            else:
                key = 'puzzleid'
        else:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if key in args:
            gid = args[key][0]
            if gid.isdigit() and gid != '0':
                self.url_type = ttype
                self.id = gid
                return True
        return False

    def download_game(self):
        # Download
        if self.id is None:
            return None
        if self.url_type == TYPE_GAME:
            url = 'https://www.redhotpawn.com/pagelet/view/game-pgn.php?gameid=%s' % self.id
        elif self.url_type == TYPE_PUZZLE:
            if '://' in self.id:
                url = self.id
                event = 'Puzzle'
            else:
                url = 'https://www.redhotpawn.com/chess-puzzles/chess-puzzle-solve.php?puzzleid=%s' % self.id
                event = 'Puzzle %s' % self.id
        else:
            return None
        page = self.download(url)
        if page is None:
            return None

        # Logic for the games
        if self.url_type == TYPE_GAME:
            # Parser
            class redhotpawnparser(HTMLParser):
                def __init__(self):
                    HTMLParser.__init__(self)
                    self.tag_ok = False
                    self.pgn = None

                def handle_starttag(self, tag, attrs):
                    if tag.lower() == 'textarea':
                        self.tag_ok = True

                def handle_data(self, data):
                    if self.pgn is None and self.tag_ok:
                        self.pgn = data

            # Extractor
            parser = redhotpawnparser()
            parser.feed(page)
            return parser.pgn.strip()

        # Logic for the puzzles
        elif self.url_type == TYPE_PUZZLE:
            pos1 = page.find('var g_startFenStr')
            if pos1 != -1:
                pos1 = page.find("'", pos1)
                pos2 = page.find("'", pos1 + 1)
                if pos2 > pos1:
                    game = {}
                    game['_url'] = url
                    game['FEN'] = page[pos1 + 1:pos2]
                    game['SetUp'] = '1'
                    game['Event'] = event
                    game['White'] = 'White'
                    game['Black'] = 'Black'
                    pos1 = page.find('<h4>')
                    pos2 = page.find('</h4>', pos1)
                    if pos1 != -1 and pos2 > pos1:
                        game['_moves'] = '{%s}' % page[pos1 + 4:pos2]
                    return self.rebuild_pgn(game)

        return None

    def get_test_links(self):
        return [('https://www.redhotpawn.com/chess/chess-game-history.php?gameid=13264954', True),                  # Game in progress (at the time of the initial test)
                ('https://www.redhotpawn.com/chess/chess-game-HISTORY.php?gameid=13261506&arg=0#anchor', True),     # Game draw
                ('https://www.redhotpawn.com/chess/chess-game-history.php?gameid=13238354', True),                  # Game stalemate
                ('https://REDHOTPAWN.com/chess/chess-GAME-analysis.php?gameid=13261541&arg=0#anchor', True),        # Game mate
                ('https://www.redhotpawn.com/chess/chess-game-history.php?gameid=1234567890', False),               # Not a game (wrong ID)
                ('https://www.redhotpawn.com/chess/view-game.php?gameid=13238354', False),                          # Not a game (wrong path in URL)
                ('https://www.redhotpawn.com/chess/chess-game-analysis.php?id=13238354', False),                    # Not a game (wrong parameter in URL)
                ('https://www.redhotpawn.com', False),                                                              # Not a game (homepage)
                ('https://www.redhotpawn.com/chess-puzzles/chess-puzzle-solve.php?puzzleid=7470', True),            # Puzzle
                ('https://www.redhotpawn.com/chess-puzzles/chess-puzzle-serve.php', True),                          # Puzzle through a random link
                ('https://www.redhotpawn.com/chess-puzzles/chess-puzzle-solve.php?puzzleid=1234567890', False)]     # Not a puzzle (wrong ID)
