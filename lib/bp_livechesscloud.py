# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface

import re
from urllib.parse import urlparse


# LiveChessCloud.com
class InternetGameLivechesscloud(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'id': re.compile(r'^[0-9a-f-]{36}$', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'LiveChessCloud.com', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() != 'view.livechesscloud.com':
            return False

        # Verify the identifier
        id = parsed.path[1:]
        if self.regexes['id'].match(id) is not None:
            self.id = id
            return True
        else:
            return False

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Fetch the host
        bourne = self.send_xhr('http://lookup.livechesscloud.com/meta/' + self.id, None)
        data = self.json_loads(bourne)
        host = self.json_field(data, 'host')
        if host == '' or (self.json_field(data, 'format') != '1'):
            return None

        # Fetch the tournament
        pgn = ''
        bourne = self.send_xhr('http://%s/get/%s/tournament.json' % (host, self.id), None)
        data = self.json_loads(bourne)
        game = {'TimeControl': self.json_field(data, 'timecontrol').replace('"', '').replace("'", ''),
                'Event': self.json_field(data, 'name'),
                'Site': ('%s %s' % (self.json_field(data, 'country'), self.json_field(data, 'location'))).strip()}
        variant = self.json_field(data, 'rules')
        if variant != 'STANDARD':
            game['Variant'] = variant
        nb_rounds = len(self.json_field(data, 'rounds', []))
        if nb_rounds == 0:
            return None

        # Fetch the rounds
        for i in range(1, nb_rounds + 1):
            bourne = self.send_xhr('http://%s/get/%s/round-%d/index.json' % (host, self.id, i), None)
            data = self.json_loads(bourne)
            game['Date'] = self.json_field(data, 'date')
            pairings = self.json_field(data, 'pairings', [])
            nb_pairings = len(pairings)
            if nb_pairings > 0:
                for j in range(nb_pairings):
                    # Players and result
                    player = pairings[j].get('white', {})
                    game['White'] = ('%s %s' % (self.json_field(player, 'lname'), self.json_field(player, 'fname'))).strip()
                    player = pairings[j].get('black', {})
                    game['Black'] = ('%s %s' % (self.json_field(player, 'lname'), self.json_field(player, 'fname'))).strip()
                    game['Result'] = self.json_field(pairings[j], 'result', '*')

                    # Fetch the moves
                    game['_moves'] = ''
                    bourne2 = self.send_xhr('http://%s/get/%s/round-%d/game-%d.json?poll=' % (host, self.id, i, j + 1), None)
                    data2 = self.json_loads(bourne2)
                    if self.json_field(data2, 'result') == 'NOTPLAYED':
                        continue
                    game['_reason'] = self.json_field(data2, 'comment')
                    moves = self.json_field(data2, 'moves')
                    for move in moves:
                        move = move.split(' ')[0]
                        game['_moves'] += '%s ' % move

                    # Game
                    candidate = self.rebuild_pgn(game)
                    if candidate is not None:
                        pgn += candidate.strip() + '\n\n'

        # Return the games
        return pgn

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('http://view.livechesscloud.com/52bd7b4f-1dd1-4bbb-a930-6417e3043b24', True),  # Games
                ('http://view.livechesscloud.com', False)]                                      # Not a game (homepage)
