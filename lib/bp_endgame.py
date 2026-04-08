# Copyright (C) 2026 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re
from urllib.parse import parse_qs

from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface


# Endgame.ai
class InternetGameEndgame(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes['url'] = re.compile(r'^https?:\/\/(\S+\.)?endgame\.ai\/game\/([0-9a-f]{9})[\/\?\#]?', re.IGNORECASE)

    def get_identity(self) -> Tuple[str, int, int]:
        return 'Endgame.ai', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        # Game ID
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = str(m.group(2))
            return True
        return False

    def download_game(self) -> Optional[str]:
        # Fetch the game
        bourne = self.send_xhr(f'https://api.endgame.ai/games/{self.id}', None)
        if bourne is None:
            return None
        chessgame = self.json_loads(bourne)

        # Build the PGN
        game = {}
        val = self.json_field(chessgame, 'tournamentId')
        if val != '':
            game['Event'] = f'Tournament {val}'
        game['Site'] = f'Game {self.id}'
        for e in self.json_field(chessgame, 'players'):
            color = 'White' if e['color'] == 'w' else 'Black'
            game[color] = self.json_field(e, 'username')
            game[f'{color}Elo'] = str(self.json_field(e, 'rating'))
            if not self.json_field(e, 'isRatingStable'):
                game[f'{color}Elo'] += '?'
        game['PlyCount'] = self.json_field(chessgame, 'movesCount')
        game['Date'] = self.json_field(chessgame, 'startedAt')[:10].replace('-', '.')
        val = self.json_field(chessgame, 'winner')
        if not self.json_field(chessgame, 'isFinished'):
            val = '*'
        elif val == 'w':
            val = '1-0'
        elif val == 'b':
            val = '0-1'
        else:
            val = '1/2-1/2'
        game['Result'] = val
        game['Termination'] = self.json_field(chessgame, 'endGameReason')
        game['TimeControl'] = self.json_field(chessgame, 'timeControl')
        game['Variant'] = self.json_field(chessgame, 'variant')
        val = self.json_field(chessgame, 'startingFen')
        if val != '':
            game['SetUp'] = '1'
            game['FEN'] = val
        game['_moves'] = ''
        for move in self.json_field(chessgame, 'moves'):
            val = parse_qs(move)
            game['_moves'] += ' ' + val['pgn'][0].strip()
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://endgame.ai/game/bcc55bd06', True),            # Game
                ('https://endgame.ai/game/zzzzzzzzz', False),           # Not a game (wrong id)
                ('https://endgame.ai', False)]                          # Not a game (homepage)
