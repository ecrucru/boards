# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_HTML
from lib.cp_interface import InternetGameInterface

import re
from urllib.parse import urlparse, parse_qs


# 365chess.com
class InternetGame365chess(InternetGameInterface):
    def get_identity(self):
        return '365chess.com', CAT_HTML

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.365chess.com', '365chess.com']:
            return False
        ppl = parsed.path.lower()
        if ppl == '/game.php':
            key = 'gid'
        elif ppl == '/view_game.php':
            key = 'g'
        else:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if key in args:
            gid = args[key][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self):
        # Download
        if self.id is None:
            return None
        url = 'https://www.365chess.com/game.php?gid=%s' % self.id
        page = self.download(url)
        if page is None:
            return None

        # Played moves
        game = {}
        pos1 = page.find("chess_game.Init({")
        pos1 = page.find(",pgn:'", pos1)
        pos2 = page.find("'", pos1 + 6)
        if -1 in [pos1, pos2]:
            return None
        game['_moves'] = page[pos1 + 6:pos2]

        # Result
        result = game['_moves'].split(' ')[-1]
        if result in ['1-0', '0-1', '1/2-1/2', '*']:
            game['Result'] = result
            game['_moves'] = " ".join(game['_moves'].split(' ')[0:-1])

        # Header
        game['_url'] = url
        lines = page.replace("<td", "\n<td").split("\n")
        rxp = re.compile(r'^([\w\-,\s]+)(\(([0-9]+)\))? vs\. ([\w\-,\s]+)(\(([0-9]+)\))?$', re.IGNORECASE)
        game['White'] = 'Unknown'
        game['Black'] = 'Unknown'
        for line in lines:
            line = line.strip()

            # Event
            for tag in ['Event', 'Site', 'Date', 'Round']:
                if tag + ':' in line:
                    pos1 = line.find(tag + ':')
                    pos1 = line.find(' ', pos1)
                    pos2 = line.find('<', pos1)
                    if -1 not in [pos1, pos2]:
                        v = line[pos1 + 1:pos2]
                        if tag == 'Date':
                            v = '%s.%s.%s' % (v[-4:], v[:2], v[3:5])  # mm/dd/yyyy --> yyyy.mm.dd
                        game[tag] = v

            # Players
            line = self.strip_html(line).strip()
            m = rxp.match(line)
            if m is not None:
                game['White'] = str(m.group(1)).strip()
                if m.group(3) is not None:
                    game['WhiteElo'] = str(m.group(3)).strip()
                game['Black'] = str(m.group(4)).strip()
                if m.group(6) is not None:
                    game['BlackElo'] = str(m.group(6)).strip()

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self):
        return [('https://www.365chess.com/view_game.php?g=4187437#anchor', True),          # Game 1/2-1/2 for special chars
                ('https://www.365chess.com/view_game.php?g=1234567890', False),             # Not a game
                ('https://www.365chess.com/game.php?gid=4230834&p=0', True)]                # Game with additional parameter
