# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, BOARD_GO, METHOD_DL
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs


# PlayOK.com
class InternetGamePlayokInterface(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'PlayOK.com', self.boardType, METHOD_DL

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.playok.com', 'playok.com']:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'g' in args:
            gid = args['g'][0]
            if gid[:2] == self.parameter:
                gid = gid[2:].replace('.txt', '')
                if gid.isdigit() and gid != '0':
                    self.id = gid
                    return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            pgn = self.download('https://www.playok.com/p/?g=%s%s.txt' % (self.parameter, self.id))
            if (pgn is not None) and (len(pgn) > 16):
                return pgn
        return None


# PlayOK.com for chess
class InternetGamePlayokChess(InternetGamePlayokInterface):
    def __init__(self):
        InternetGamePlayokInterface.__init__(self)
        self.boardType = BOARD_CHESS
        self.parameter = 'ch'

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://www.playok.com/p/?g=ch532424172', True),       # Game
                ('https://PLAYOK.com/p/?g=ch532424172.txt', True),      # Game (direct link)
                ('http://www.playok.com/p/?g=ch484680868', False),      # Not a game (expired game)
                ('https://PLAYOK.com/p/?g=ch999999999#tag', False),     # Not a game (wrong ID)
                ('http://www.playok.com/p/?g=go15733322#165', False),   # Not a game (go)
                ('http://www.playok.com', False)]                       # Not a game (homepage)


# PlayOK.com for go
class InternetGamePlayokGo(InternetGamePlayokInterface):
    def __init__(self):
        InternetGamePlayokInterface.__init__(self)
        self.boardType = BOARD_GO
        self.parameter = 'go'

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://www.playok.com/p/?g=go18495831#17', True),     # Game
                ('https://PLAYOK.com/p/?g=go18495831.txt', True),       # Game (direct link)
                ('https://PLAYOK.com/p/?g=go999999999#tag', False),     # Not a game (wrong ID)
                ('http://www.playok.com/p/?g=ch484680868', False),      # Not a game (chess)
                ('http://www.playok.com', False)]                       # Not a game (homepage)
