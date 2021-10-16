# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import List, Tuple

from lib.bp_libase import InternetGameLibase


# Lishogi.org
class InternetGameLishogi(InternetGameLibase):
    def __init__(self):
        InternetGameLibase.__init__(self)
        self.set_options_li('lishogi.org', 'shogi', True, 'kif', 'LishogiPuzzle(')
        self.allow_extra = False
        self.use_sanitization = False

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://lishogi.org/X0Logbra#tag', True),             # Game (with tag)
                ('https://lishogi.org/X0Logbra/gote', True),            # Game (from side)
                ('https://lishogi.org/X0LOGBRA', False),                # Not a game (wrong ID)
                ('https://lishogi.org/study/lSHbX5Tv', True),           # Study
                ('https://lishogi.org/training/mQtix', True),           # Puzzle
                ('https://lishogi.org/training/ABCDE', False),          # Not a puzzle (wrong ID)
                ('https://lishogi.org/training/tsume', True),           # Thematic puzzle
                ('https://lishogi.org/tournament/bpaWaCPU', True),      # Tournament
                ('https://lishogi.org/tournament/abcdefgh', False),     # Tournament (wrong ID)
                ]                                                       # Broadcast, Practice, Swiss
