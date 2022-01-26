# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, Dict, Tuple
from lib.const import BOARD_CHESS, METHOD_DL, TYPE_GAME, TYPE_PUZZLE, TYPE_STUDY, TYPE_SWISS, TYPE_TOURNAMENT
from lib.bp_interface import InternetGameInterface

import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import chess


# Base for the clones of Lichess
class InternetGameLibase(InternetGameInterface):
    def set_options_li(self, host: str, variant: str, api: bool, ext: str, puzzle_tag: str) -> None:
        # Options
        self._host = host
        self._variant = variant
        self._use_api = api
        self._ext = ext
        self._puzzle_tag = puzzle_tag

        # Initialization
        hreg = self._host.replace('.', '\\.')
        self.regexes.update({'broadcast': re.compile(r'^https?:\/\/(\S+\.)?%s\/broadcast\/[a-z0-9\-]+\/([a-z0-9]{8})[\/\?\#]?' % hreg, re.IGNORECASE),
                             'game': re.compile(r'^https?:\/\/(\S+\.)?%s\/(game\/export\/|embed\/)?([a-z0-9]{8})\/?([\S\/]+)?$' % hreg, re.IGNORECASE),
                             'practice': re.compile(r'^https?:\/\/(\S+\.)?%s\/practice\/[\w\-\/]+\/([a-z0-9]{8}\/[a-z0-9]{8})(\.%s)?\/?([\S\/]+)?$' % (hreg, self._ext), re.IGNORECASE),
                             'puzzle': re.compile(r'^https?:\/\/(\S+\.)?%s\/training\/([a-z0-9]+\/)?([a-z0-9]+)[\/\?\#]?' % hreg, re.IGNORECASE),
                             'study': re.compile(r'^https?:\/\/(\S+\.)?%s\/study\/([a-z0-9]{8}(\/[a-z0-9]{8})?)(\.%s)?\/?([\S\/]+)?$' % (hreg, self._ext), re.IGNORECASE),
                             'swiss': re.compile(r'^https?:\/\/(\S+\.)?%s\/swiss\/([a-z0-9]{8})[\/\?\#]?' % hreg, re.IGNORECASE),
                             'tournament': re.compile(r'^https?:\/\/(\S+\.)?%s\/tournament\/([a-z0-9]{8})[\/\?\#]?' % hreg, re.IGNORECASE)})

    def get_identity(self) -> Tuple[str, int, int]:
        return self._host.capitalize(), BOARD_CHESS, METHOD_DL

    def assign_game(self, url: str) -> bool:
        for name, typ, pid in [('broadcast', TYPE_STUDY, 2),
                               ('practice', TYPE_STUDY, 2),
                               ('puzzle', TYPE_PUZZLE, 3),
                               ('study', TYPE_STUDY, 2),
                               ('swiss', TYPE_SWISS, 2),
                               ('tournament', TYPE_TOURNAMENT, 2),
                               ('game', TYPE_GAME, 3),                  # Order matters
                               ]:
            if name in self.regexes:
                m = self.regexes[name].match(url)
                if m is not None:
                    self.url_type = typ
                    self.id = m.group(pid)
                    return True
        return False

    def query_api(self, path: str) -> Optional[Dict]:
        if not self._use_api:
            return None
        try:
            response = urlopen(Request('https://%s%s' % (self._host, path), headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/vnd.lichess.v4+json'}))
            bourne = self.read_data(response)
            return self.json_loads(bourne)
        except HTTPError:
            return None

    def download_game(self) -> Optional[str]:
        # Check
        if None in [self.id, self._host]:
            return None

        # Logic for the studies
        if self.url_type == TYPE_STUDY:
            return self.download('https://%s/study/%s.%s' % (self._host, self.id, self._ext), userAgent=True)

        # Logic for the swiss tournaments
        elif self.url_type == TYPE_SWISS:
            return self.download('https://%s/api/swiss/%s/games' % (self._host, self.id))

        # Logic for the tournaments
        elif self.url_type == TYPE_TOURNAMENT:
            return self.download('https://%s/api/tournament/%s/games' % (self._host, self.id), userAgent=True)

        # Logic for the games
        elif self.url_type == TYPE_GAME:
            # Download the finished game
            api = self.query_api('/import/master/%s/white' % self.id)
            game = self.json_field(api, 'game')
            if (api is None) or ('winner' in game):
                url = 'https://%s/game/export/%s?literate=1' % (self._host, self.id)
                return self.download(url)
            else:
                if not self.allow_extra and game['rated']:
                    return None

            # Rebuild the PGN file
            game = {}
            game['_url'] = 'https://%s%s' % (self._host, self.json_field(api, 'url/round'))
            game['Variant'] = self.json_field(api, 'game/variant/name')
            game['FEN'] = self.json_field(api, 'game/initialFen')
            game['SetUp'] = '1'
            game['White'] = self.json_field(api, 'player/name', self.json_field(api, 'player/user/username', 'Anonymous'))
            game['WhiteElo'] = self.json_field(api, 'player/rating')
            game['Black'] = self.json_field(api, 'opponent/name', self.json_field(api, 'opponent/user/username', 'Anonymous'))
            game['BlackElo'] = self.json_field(api, 'opponent/rating')
            if self.json_field(api, 'clock') != '':
                game['TimeControl'] = '%d+%d' % (self.json_field(api, 'clock/initial'), self.json_field(api, 'clock/increment'))
            else:
                game['TimeControl'] = '%dd' % (self.json_field(api, 'correspondence/increment') // 86400)
            game['Result'] = '*'
            game['_moves'] = ''
            moves = self.json_field(api, 'steps')
            for move in moves:
                if move['ply'] > 0:
                    game['_moves'] += ' %s' % move['san']
            return self.rebuild_pgn(game)

        # Logic for the puzzles
        elif self.url_type == TYPE_PUZZLE:
            # Fetch the puzzle
            url = 'https://%s/training/%s' % (self._host, self.id)
            page = self.download(url)
            if page is None:
                return None

            # Extract the JSON
            page = page.replace("\n", '')
            pos1 = page.find(self._puzzle_tag)
            if pos1 == -1:
                return None
            pos1 = page.find('"game"', pos1 + 1)
            if pos1 == -1:
                return None
            c = 1
            pos2 = pos1
            while pos2 < len(page):
                pos2 += 1
                if page[pos2] == '{':
                    c += 1
                if page[pos2] == '}':
                    c -= 1
                if c == 0:
                    break
            if c != 0:
                return None

            # Header
            bourne = page[pos1 - 1:pos2 + 1]
            chessgame = self.json_loads(bourne)
            puzzle = self.json_field(chessgame, 'puzzle')
            if puzzle == '':
                return None
            game = {}
            game['_url'] = 'https://%s/%s' % (self._host, self.json_field(chessgame, 'game/id'))
            game['Site'] = self._host
            rating = self.json_field(puzzle, 'rating')
            game['Event'] = 'Puzzle %s, rated %d' % (self.json_field(puzzle, 'id'), rating)
            game['Result'] = '*'
            game['Annotator'] = self.json_field(chessgame, 'game/author')
            game['X_TimeControl'] = self.json_field(chessgame, 'game/clock')
            game['X_Rating'] = rating
            fen = self.json_field(chessgame, 'game/fen')
            if fen != '':
                game['Variant'] = self._variant
                game['FEN'] = fen
                game['SetUp'] = '1'

            # Players
            players = self.json_field(chessgame, 'game/players')
            if isinstance(players, list):
                for p in players:
                    if p['color'] == 'white':
                        t = 'White'
                    elif p['color'] == 'black':
                        t = 'Black'
                    else:
                        return None
                    pos1 = p['name'].find(' (')
                    if pos1 == -1:
                        game[t] = p['name']
                    else:
                        game[t] = p['name'][:pos1]
                        game[t + 'Elo'] = p['name'][pos1 + 2:-1]

            # Moves and solution
            solution = self.json_field(chessgame, 'puzzle/solution')
            if isinstance(solution, list) and ('FEN' in game):
                game['_moves'] = '{Solution: %s}' % ' '.join(solution)
            else:
                # Current position
                if self._variant != '':
                    return None
                board = chess.Board()
                game['_moves'] = self.json_field(chessgame, 'game/pgn')
                moves = game['_moves'].split(' ')
                for move in moves:
                    board.push_san(move)
                game['_url'] += '#%d' % len(moves)

                # Moves
                game['_moves'] += ' {Solution: '
                moves = self.json_field(puzzle, 'solution')
                for move in moves:
                    kmove = chess.Move.from_uci(move)
                    game['_moves'] += board.san(kmove) + ' '
                    board.push(kmove)
                game['_moves'] = game['_moves'].strip() + '}'

            # Rebuild the PGN game
            return self.rebuild_pgn(game)

        else:
            assert(False)
