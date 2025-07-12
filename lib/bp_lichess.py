# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import List, Tuple

from lib.bp_libase import InternetGameLibase


# Lichess.org
class InternetGameLichess(InternetGameLibase):
    def __init__(self):
        InternetGameLibase.__init__(self)
        self.set_options_li('lichess.org', '', True, 'pgn', 'id="page-init-data"')

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://lichess.org/CA4bR2b8/black/analysis#12', True),                            # Game in advanced position
                ('https://lichess.org/CA4bR2b8', True),                                             # Canonical address
                ('CA4bR2b8', False),                                                                # Short ID (possible via the generic function only)
                ('https://lichess.org/game/export/CA4bR2b8', True),                                 # Download link
                ('https://LICHESS.org/embed/CA4bR2b8/black?theme=brown', True),                     # Embedded game
                ('http://fr.lichess.org/@/thibault', False),                                        # Not a game (user page)
                ('http://lichess.org/blog', False),                                                 # Not a game (page)
                ('http://lichess.dev/ABCD1234', False),                                             # Not a game (wrong ID)
                ('https://lichess.org/9y4KpPyG', True),                                             # Variant game Chess960
                ('https://LICHESS.org/nGhOUXdP?p=0', True),                                         # Variant game with parameter
                ('https://lichess.org/nGhOUXdP?p=0#3', True),                                       # Variant game with parameter and anchor
                ('https://hu.lichess.org/study/hr4H7sOB?page=1', True),                             # Study of one game with unused parameter
                ('https://lichess.org/study/76AirB4Y/C1NcczQl', True),                              # Chapter of a study
                ('https://lichess.org/study/hr4H7sOB/fvtzEXvi.pgn#32', True),                       # Chapter of a study with anchor
                ('https://lichess.org/STUDY/hr4H7sOB.pgn', True),                                   # Study of one game
                ('https://lichess.org/training/daily', True),                                       # Daily puzzle
                ('https://lichess.org/training/lfSgX', True),                                       # Puzzle
                ('https://lichess.org/fr/training/lfSgX', True),                                    # Puzzle with language
                ('https://lichess.org/training/mix/fmH0k', True),                                   # Puzzle from a random theme
                ('https://lichess.org/training/attackingF2F7/9LaN9', True),                         # Puzzle from a given theme
                ('https://lichess.org/training/84969', False),                                      # Not a puzzle (old ID)
                ('https://lichess.org/training/1281301832', True),                                  # Puzzle (wrong ID but redirected to a valid puzzle)
                ('https://lichess.org/broadcast/2019-gct-zagreb-round-4/jQ1dbbX9', True),           # Broadcast
                ('https://lichess.org/broadcast/2019-pychess-round-1/pychess1', False),             # Not a broadcast (wrong ID)
                ('https://lichess.ORG/practice/basic-tactics/the-pin/9ogFv8Ac/BRmScz9t#t', True),   # Practice
                ('https://lichess.org/practice/py/chess/12345678/abcdEFGH', False),                 # Not a practice (wrong ID)
                ('https://lichess.org/swiss/vQTjVdJU#tag', True),                                   # Swiss tournament
                ('https://lichess.org/swiss/VQTJVDJU#tag', False),                                  # Not a swiss tournament (wrong ID)
                ('https://lichess.org/tournament/OzTsVueX?arg=1', True),                            # Tournament
                ('https://lichess.org/tournament/OZTSVUEX', False)]                                 # Not a tournament (wrong ID)
