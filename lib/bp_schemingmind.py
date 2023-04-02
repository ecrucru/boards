# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from urllib.parse import urlparse, parse_qs

from lib.const import BOARD_CHESS, METHOD_DL
from lib.bp_interface import InternetGameInterface


# SchemingMind.com
class InternetGameSchemingmind(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'SchemingMind.com', BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        # Verify the host
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.schemingmind.com', 'schemingmind.com']:
            return False

        # Read the identifier
        if 'game.aspx' in parsed.path:
            args = parse_qs(parsed.query)
            if 'game_id' in args:
                gid = args['game_id'][0]
                if gid.isdigit() and (gid != '0'):
                    self.id = gid
                    return True
        return False

    def download_game(self) -> Optional[str]:
        if self.id is not None:
            return self.download('https://www.schemingmind.com/home/game.aspx?game_id=%s&view=3' % self.id)
        return None

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.schemingmind.com/home/game.aspx?game_id=457237', True),           # Game (Alice chess)
                ('https://www.schemingmind.com/home/game.aspx?game_id=722914&view=3', True),    # Game (upside down chess)
                ('https://www.schemingmind.com/game.aspx?game_id=35343', True),                 # Game (chicken chess)
                ('https://www.schemingmind.com/invalid-path/game.aspx?game_id=715718', True),   # Game (kriegspiel chess)
                ('https://www.schemingmind.com/game.aspx?game_id=9876543210', False),           # Not a game (wrong id)
                ('https://www.schemingmind.com', False)]                                        # Not a game (homepage)
