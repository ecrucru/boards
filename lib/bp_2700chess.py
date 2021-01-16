# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# 2700chess.com
class InternetGame2700chess(InternetGameInterface):
    def get_identity(self):
        return '2700chess.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url):
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.2700chess.com', '2700chess.com']:
            return False

        # Refactor the direct link
        if parsed.path.lower() == '/games/download':
            args = parse_qs(parsed.query)
            if 'slug' in args:
                self.id = 'https://2700chess.com/games/%s' % args['slug'][0]
                return True

        # Verify the path
        if parsed.path.startswith('/games/'):
            self.id = url
            return True
        else:
            return False

    def download_game(self):
        # Download
        if self.id is None:
            return None
        page = self.download(self.id)
        if page is None:
            return None

        # Extract the PGN
        lines = page.split(';')
        for line in lines:
            if 'analysis.setPgn(' in line:
                pos1 = line.find('"')
                if pos1 != -1:
                    pos2 = pos1
                    while pos2 < len(line):
                        pos2 += 1
                        if line[pos2] == '"' and line[pos2 - 1:pos2 + 1] != '\\"':
                            pgn = line[pos1 + 1:pos2]
                            return pgn.replace('\\"', '"').replace('\\/', '/').replace('\\n', "\n").strip()
        return None

    def get_test_links(self):
        return [('https://2700CHESS.com/games/dominguez-perez-yu-yangyi-r19.6-hengshui-chn-2019-05-18', True),                      # Game
                ('https://2700chess.com/games/download?slug=dominguez-perez-yu-yangyi-r19.6-hengshui-chn-2019-05-18#tag', True),    # Game with direct link
                ('https://2700chess.COM/games/pychess-r1.1-paris-fra-2019-12-25', False),                                           # Not a game (wrong ID)
                ('https://2700chess.com', False)]                                                                                   # Not a game (homepage)
