# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from urllib.parse import urlparse, parse_qs

from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface


# LiveChess.aunz.net
class InternetGameLivechessAunz(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'src': re.compile(r"src=\"([^\"]+)\"", re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'LiveChess.aunz.net', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, 'livechess.aunz.net')

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Download the page
        page = self.download(self.id)
        if page is None:
            page = 'src="%s"' % self.id

        # Find the game ID
        gid = None
        for url in self.regexes['src'].findall(page):
            parsed = urlparse(url)
            if parsed.netloc.lower() == 'livechess.aunz.net':
                args = parse_qs(parsed.query)
                if 'tourn' in args:
                    gid = args['tourn'][0]
                    if gid != '':
                        break
        if gid in [None, '']:
            return None

        # Fetch the headers of the games
        api = 'https://livechess.aunz.net/viewer/chess.php?t=%s&getGameList=1&pgnFile=%s.LOCAL_FILE' % (gid, gid)
        bourne = self.send_xhr(api, None)
        headers = self.json_loads(bourne)
        if (headers is None) or (len(headers) == 0):
            return None

        # Fetch the games
        buffer = ''
        for i in range(len(headers)):
            api = 'https://livechess.aunz.net/viewer/chess.php?t=%s&getGameDetails=1&pgnFile=%s.LOCAL_FILE&gameIndex=%d' % (gid, gid, i)
            bourne = self.send_xhr(api, None)
            data = self.json_loads(bourne)
            if data is None:
                continue

            # Build the game
            game = {}
            game['_url'] = self.id
            for k in ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result', 'TimeControl']:
                game[k] = self.json_field(data, k.lower())

            game['_moves'] = ''
            moves = self.json_field(data, 'moves')
            for k in moves:
                game['_moves'] += '%s ' % self.json_field(moves[k], 'white/move')
                game['_moves'] += '%s ' % self.json_field(moves[k], 'black/move')

            buffer += self.rebuild_pgn(game) + '\n\n'
        return buffer

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://livechess.aunz.net/oceania-zonal-2023-playoffs/', True),                                                          # Tournament (short)
                ('https://livechess.aunz.net/tournament-archive/tournament-archive-2022/2022-queensland-championships/view-games/', True),  # Tournament (long)
                ('https://livechess.aunz.net/viewer/live.php?tourn=QC-2022', True),                                                         # Tournament (inner frame)
                ('https://livechess.aunz.net/viewer/live.php?tourn=QC-1922', False),                                                        # Not a game (wrong ID)
                ('https://livechess.aunz.net', False)]                                                                                      # Not a game (homepage)
