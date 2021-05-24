# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface

import re
from urllib.parse import unquote
import chess


# SchachArena.de
class InternetGameSchacharena(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'player': re.compile(r'.*spielerstatistik.*name=([%\w]+).*\[([0-9]+)\].*', re.IGNORECASE),
                             'move': re.compile(r'.*<span.*onMouseOut.*fan\(([0-9]+)\).*', re.IGNORECASE),
                             'result': re.compile(r'.*<strong>(1:0|0:1|&frac12;)<\/strong>.*', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'SchachArena.de', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        return self.reacts_to(url, 'schacharena.de')

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Download page
        page = self.download(self.id)
        if page is None:
            return None

        # Parse
        player_count = 0
        game = {}
        game['Result'] = '*'
        game['_moves'] = ''
        game['_url'] = self.id
        board = chess.Board()
        lines = page.split("\n")
        for line in lines:
            # Player
            m = self.regexes['player'].match(line)
            if m is not None:
                player_count += 1
                if player_count == 1:
                    tag = 'White'
                elif player_count == 2:
                    tag = 'Black'
                else:
                    return None
                game[tag] = unquote(m.group(1), encoding='latin-1')
                game[tag + 'Elo'] = m.group(2)
                continue

            # Move
            m = self.regexes['move'].match(line)
            if m is not None:
                move = m.group(1)
                move = '_abcdefgh'[int(move[0])] + move[1] + '_abcdefgh'[int(move[2])] + move[3]
                kmove = chess.Move.from_uci(move)
                game['_moves'] += '%s ' % board.san(kmove)
                board.push(kmove)
                continue

            # Result
            m = self.regexes['result'].match(line)
            if m is not None:
                game['Result'] = m.group(1).replace(':', '-').replace('&frac12;', '1/2-1/2')
                continue

        # Final PGN
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://www.schacharena.de/new/verlauf_db_new.php?name=Lolle2008&gedreht=0&nr=6578', True),       # Game (1-0)
                ('https://www.schacharena.de/new/verlauf_db_new.php?name=Lolle2008&gedreht=1&nr=6572', True),       # Game (0-1)
                ('https://www.schacharena.de/new/verlauf_db_new.php?name=lutz53&gedreht=0&nr=23489', True),         # Game (1/2)
                ('https://www.schacharena.de/new/verlauf_db_new.php?name=k%F6nig123456&gedreht=0&nr=41440', True),  # Game (special caracter)
                ('https://www.schacharena.de/new/spielerstatistik.php?name=Umex', False),                           # Not a game (user page)
                ('https://www.schacharena.de', False)]                                                              # Not a game (home page)
