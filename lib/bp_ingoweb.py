# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# Ingo-web.com
class InternetGameIngoweb(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'Ingo-web.com', BOARD_GO, METHOD_DL

    def assign_game(self, url: str) -> bool:
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() in ['www.ingo-web.com', 'ingo-web.com']:
            # Read the arguments
            args = parse_qs(parsed.query)
            if 'gid' in args:
                gid = args['gid'][0]
                if gid.isdigit() and len(gid) == 14:
                    self.id = gid
                    return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            data = self.download('https://ingo-web.com/jsgo.cgi?m=download&gid=%s' % self.id)
            if data != '':
                return data
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://ingo-WEB.com/jsgo.cgi?m=obs&gid=20201213155606', True),       # Game
                ('http://ingo-web.com/jsgo.cgi?m=download&gid=20201213155606', True),   # Download link
                ('https://ingo-web.com/jsgo.cgi?m=obs&gid=20200913144432', False),      # Not a game (unknown game)
                ('https://ingo-web.com/jsgo.cgi?m=obs&gid=123456', False),              # Not a game (invalid id)
                ('https://ingo-web.com', False)]                                        # Not a game (homepage)
