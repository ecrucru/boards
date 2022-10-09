# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface

import re
from base64 import b64decode
from json import dumps


# IdeaChess.com
class InternetGameIdeachess(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/(\S+\.)?ideachess\.com\/.*\/.*\/([0-9]+)[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'IdeaChess.com', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        # Game ID
        m = self.regexes['url'].match(url)
        if m is not None:
            gid = str(m.group(2))
            if gid.isdigit() and gid != '0':
                # Game type
                classification = [('/chess_tactics_puzzles/checkmate_n/', 'm'),
                                  ('/echecs_tactiques/mat_n/', 'm'),
                                  ('/scacchi_tattica/scacco_matto_n/', 'm'),
                                  ('/chess_tactics_puzzles/tactics_n/', 't'),
                                  ('/echecs_tactiques/tactiques_n/', 't'),
                                  ('/scacchi_tattica/tattica_n/', 't')]
                for path, ttyp in classification:
                    if path in url.lower():
                        self.url_type = ttyp
                        self.id = gid
                        return True
        return False

    def download_game(self) -> Optional[str]:
        # Check
        if self.url_type is None or self.id is None:
            return None

        # Fetch the puzzle
        api = 'http://www.ideachess.com/com/ajax2'
        data = {'message': dumps({'action': 100,
                                  'data': {'problemNumber': int(self.id),
                                           'kind': self.url_type}},
                                 separators=(',', ':'))}
        bourne = self.send_xhr(api, data)
        chessgame = self.json_loads(bourne)
        if self.json_field(chessgame, 'action') != 200:
            return None

        # Build the PGN
        game = {}
        if self.url_type == 'm':
            game['_url'] = 'http://www.ideachess.com/chess_tactics_puzzles/checkmate_n/%s' % self.id
        elif self.url_type == 't':
            game['_url'] = 'http://www.ideachess.com/chess_tactics_puzzles/tactics_n/%s' % self.id
        else:
            assert(False)
        game['FEN'] = b64decode(self.json_field(chessgame, 'data/FEN')).decode().strip()
        game['SetUp'] = '1'
        game['_moves'] = self.json_field(chessgame, 'data/PGN')
        v = self.json_field(chessgame, 'data/requiredMoves')
        if v > 0:
            game['Site'] = '%d moves to find' % v
        list = self.json_field(chessgame, 'data/extraInfo').split('|')
        if len(list) == 4:
            game['Event'] = list[0][list[0].find(' ') + 1:].strip()
            game['Date'] = list[1].strip()
            l2 = list[2].split(' - ')
            if len(l2) == 2:
                game['White'] = l2[0].strip()
                game['Black'] = l2[1].strip()
            game['Result'] = list[3].strip()
        else:
            game['Result'] = '*'
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://www.ideachess.com/chess_tactics_puzzles/checkmate_n/37431', True),             # Mate EN
                ('http://fr.ideachess.com/echecs_tactiques/mat_n/37431', True),                         # Mate FR
                ('http://it.ideachess.com/scacchi_tattica/scacco_matto_n/37431', True),                 # Mate IT
                ('http://de.ideachess.com/chess_tactics_puzzles/checkmate_n/37431', True),              # Mate DE
                ('http://es.ideachess.com/chess_tactics_puzzles/checkmate_n/37431', True),              # Mate ES
                ('http://nl.ideachess.com/chess_tactics_puzzles/checkmate_n/37431', True),              # Mate NL
                ('http://ru.ideachess.com/chess_tactics_puzzles/checkmate_n/37431', True),              # Mate RU
                ('http://www.ideachess.com/chess_tactics_puzzles/tactics_n/32603', True),               # Tactics EN
                ('http://fr.ideachess.com/echecs_tactiques/tactiques_n/32603', True),                   # Tactics FR
                ('http://it.ideachess.com/scacchi_tattica/tattica_n/32603', True),                      # Tactics IT
                ('http://de.ideachess.com/chess_tactics_puzzles/tactics_n/32603', True),                # Tactics DE
                ('http://es.ideachess.com/chess_tactics_puzzles/tactics_n/32603', True),                # Tactics ES
                ('http://nl.ideachess.com/chess_tactics_puzzles/tactics_n/32603', True),                # Tactics NL
                ('http://ru.ideachess.com/chess_tactics_puzzles/tactics_n/32603', True),                # Tactics RU
                ('http://www.ideachess.com/chess_tactics_puzzles/checkmate_n/123457890', False),        # Not a mate (wrong ID)
                ('http://www.ideachess.com/chess_tactics_puzzles/tactics_n/123457890', False),          # Not a tactics (wrong ID)
                ('http://www.ideachess.com', False)]                                                    # Not a puzzle (homepage)
