# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface

import re
from urllib.parse import urlparse


# ChessVariants.training
class InternetGameChessvariants(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'id': re.compile(r'\/Puzzle\/([0-9]+)', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessVariants.training', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        # Verify the hostname
        parsed = urlparse(url)
        if parsed.netloc.lower() != 'chessvariants.training':
            return False

        # Verify the identifier
        m = self.regexes['id'].search(url)
        if m is None:
            return False
        self.id = m.group(1)
        return True

    def download_game(self) -> Optional[str]:
        # Check
        if self.id is None:
            return None

        # Fetch the puzzle
        data = {'id': self.id}
        bourne = self.send_xhr('https://chessvariants.training/Puzzle/Train/Setup',
                               data, origin='https://chessvariants.training')
        data = self.json_loads(bourne)
        if self.json_field(data, 'success') is False:
            return None

        # Prepare the game
        game = {'White': 'White',
                'Black': 'Black',
                'Result': '*',
                'Annotator': self.json_field(data, 'author'),
                'SetUp': '1',
                'FEN': self.json_field(data, 'fen'),
                'Variant': self.json_field(data, 'variant'),
                '_url': self.json_field(data, 'additionalInfo')}
        session = self.json_field(data, 'trainingSessionId')

        # Fetch the solution from random moves
        for i in range(8):
            cfrom = self.json_field(data, 'dests/*')
            cto = self.json_field(data, 'dests/%s/[0]' % cfrom)
            data = {'id': self.id,
                    'trainingSessionId': session,
                    'origin': cfrom,
                    'destination': cto}
            bourne = self.send_xhr('https://chessvariants.training/Puzzle/Train/SubmitMove',
                                   data, origin='https://chessvariants.training')
            data = self.json_loads(bourne)
            if 'replayMoves' in data:
                break

        # Store the solution
        moves = self.json_field(data, 'replayMoves')
        moves = [e.replace('-', '') for e in moves if e is not None]
        game['_moves'] = '{%s}' % (' '.join(moves))
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chessvariants.training/Puzzle/7874', True),       # Puzzle (1 level)
                ('https://chessvariants.training/Puzzle/14453', True),      # Puzzle (more levels)
                ('https://chessvariants.training/Puzzle/999999', False),    # Not a puzzle (wrong ID)
                ('http://chessvariants.training', False)]                   # Not a game (homepage)
