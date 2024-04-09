# Copyright (C) 2024 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
import re

from lib.const import BOARD_CHESS, METHOD_API
from lib.bp_interface import InternetGameInterface


# ChessVsGPT.com
class InternetGameChessvsgpt(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'url': re.compile(r'^https?:\/\/chessvsgpt\.com\/game\/([0-9a-f]{24})[\/\?\#]?', re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return 'ChessVsGPT.com', BOARD_CHESS, METHOD_API

    def assign_game(self, url: str) -> bool:
        m = self.regexes['url'].match(url)
        if m is not None:
            self.id = str(m.group(1))
            return True
        return False

    def download_game(self) -> Optional[str]:
        # Qery the API
        if self.id is None:
            return None
        xhr = self.download('https://devapi.chessvsgpt.com/games/%s' % self.id)
        if xhr is None:
            return None
        data = self.json_loads(xhr)

        # Rebuild the PGN game
        game = {}
        game['_url'] = 'The game is full of illegal moves!'
        game['Date'] = self.json_field(data, 'startedAt')[:10].replace('-', '.')
        game['White'] = 'Human' if self.json_field(data, 'ai') == 'black' else 'AI'
        game['Black'] = 'Human' if game['White'] == 'AI' else 'AI'
        winner = self.json_field(data, 'winner')
        game['Result'] = '1-0' if winner == 'white' else ('0-1' if winner == 'black' else '*')

        # Moves
        game['_moves'] = '{'
        moves = self.json_field(data, 'moves')
        for i, m in enumerate(moves):
            if i % 2 == 0:
                game['_moves'] += '%d. ' % (i // 2 + 1)
            game['_moves'] += '%s ' % m
        game['_moves'] += '}'
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chessvsgpt.com/game/65f7af1409f35429106f2a8c', True)]
