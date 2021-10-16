# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import List, Tuple

from lib.bp_libase import InternetGameLibase


# MskChess.ru
class InternetGameMskchess(InternetGameLibase):
    def __init__(self):
        InternetGameLibase.__init__(self)
        self.set_options_li('MskChess.ru', '', True, 'pgn', 'Unsupported-Training')

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://mskchess.ru/jvcVna2g?arg', True),         # Game
                ('https://MSKCHESS.ru/jvcVna2g/black#tag', True),   # Game (from black side)
                ('https://mskchess.ru/training/61185', False),      # Puzzle (unsupported old version of Lichess)
                ('https://mskchess.ru/tournament/Hv8CH43E', True)   # Tournament
                ]                                                   # Study, Broadcast, Practice, Swiss
