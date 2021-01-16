# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_DL, TYPE_GAME, TYPE_PUZZLE, TYPE_STUDY
from lib.bp_interface import InternetGameInterface

import re
from urllib.request import Request, urlopen


# Lichess.org
class InternetGameLichess(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'broadcast': re.compile(r'^https?:\/\/(\S+\.)?lichess\.(org|dev)\/broadcast\/[a-z0-9\-]+\/([a-z0-9]+)[\/\?\#]?', re.IGNORECASE),
                             'game': re.compile(r'^https?:\/\/(\S+\.)?lichess\.(org|dev)\/(game\/export\/|embed\/)?([a-z0-9]+)\/?([\S\/]+)?$', re.IGNORECASE),
                             'practice': re.compile(r'^https?:\/\/(\S+\.)?lichess\.(org|dev)\/practice\/[\w\-\/]+\/([a-z0-9]+\/[a-z0-9]+)(\.pgn)?\/?([\S\/]+)?$', re.IGNORECASE),
                             'puzzle': re.compile(r'^https?:\/\/(\S+\.)?lichess\.(org|dev)\/training\/([0-9]+|daily)[\/\?\#]?', re.IGNORECASE),
                             'study': re.compile(r'^https?:\/\/(\S+\.)?lichess\.(org|dev)\/study\/([a-z0-9]+(\/[a-z0-9]+)?)(\.pgn)?\/?([\S\/]+)?$', re.IGNORECASE)})

    def reset(self):
        InternetGameInterface.reset(self)
        self.url_tld = 'org'

    def get_identity(self):
        return 'Lichess.org', BOARD_CHESS, METHOD_DL

    def assign_game(self, url):
        # Retrieve the ID of the broadcast
        m = self.regexes['broadcast'].match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) == 8:
                self.url_type = TYPE_STUDY
                self.id = gid
                self.url_tld = m.group(2)
                return True

        # Retrieve the ID of the practice
        m = self.regexes['practice'].match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) == 17:
                self.url_type = TYPE_STUDY
                self.id = gid
                self.url_tld = m.group(2)
                return True

        # Retrieve the ID of the study
        m = self.regexes['study'].match(url)
        if m is not None:
            gid = m.group(3)
            if len(gid) in [8, 17]:
                self.url_type = TYPE_STUDY
                self.id = gid
                self.url_tld = m.group(2)
                return True

        # Retrieve the ID of the puzzle
        m = self.regexes['puzzle'].match(url)
        if m is not None:
            gid = m.group(3)
            if (gid.isdigit() and gid != '0') or gid == 'daily':
                self.url_type = TYPE_PUZZLE
                self.id = gid
                self.url_tld = m.group(2)
                return True

        # Retrieve the ID of the game
        m = self.regexes['game'].match(url)
        if m is not None:
            gid = m.group(4)
            if len(gid) == 8:
                self.url_type = TYPE_GAME
                self.id = gid
                self.url_tld = m.group(2)
                return True

        # Nothing found
        return False

    def query_api(self, path):
        response = urlopen(Request('https://lichess.%s%s' % (self.url_tld, path), headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/vnd.lichess.v4+json'}))
        bourne = self.read_data(response)
        return self.json_loads(bourne)

    def download_game(self):
        # Check
        if None in [self.id, self.url_tld]:
            return None

        # Logic for the games
        if self.url_type == TYPE_GAME:
            # Download the finished game
            api = self.query_api('/import/master/%s/white' % self.id)
            game = self.json_field(api, 'game')
            if 'winner' in game:
                url = 'https://lichess.%s/game/export/%s?literate=1' % (self.url_tld, self.id)
                return self.download(url)
            else:
                if not self.allow_extra and game['rated']:
                    return None

            # Rebuild the PGN file
            game = {}
            game['_url'] = 'https://lichess.%s%s' % (self.url_tld, self.json_field(api, 'url/round'))
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

        # Logic for the studies
        elif self.url_type == TYPE_STUDY:
            url = 'https://lichess.%s/study/%s.pgn' % (self.url_tld, self.id)
            return self.download(url, userAgent=True)

        # Logic for the puzzles
        elif self.url_type == TYPE_PUZZLE:
            # The API doesn't provide the history of the moves
            # chessgame = self.query_api('/training/%s/load' % self.id)

            # Fetch the puzzle
            url = 'https://lichess.%s/training/%s' % (self.url_tld, self.id)
            page = self.download(url)
            if page is None:
                return None

            # Extract the JSON
            page = page.replace("\n", '')
            pos1 = page.find("lichess.puzzle =")
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
            game['_url'] = 'https://lichess.%s/%s#%s' % (self.url_tld, self.json_field(puzzle, 'gameId'), self.json_field(puzzle, 'initialPly'))
            game['Site'] = 'lichess.%s' % self.url_tld
            rating = self.json_field(puzzle, 'rating')
            game['Event'] = 'Puzzle %d, rated %s' % (self.json_field(puzzle, 'id'), rating)
            game['Result'] = '*'
            game['X_ID'] = self.json_field(puzzle, 'id')
            game['X_TimeControl'] = self.json_field(chessgame, 'game/clock')
            game['X_Rating'] = rating
            game['X_Attempts'] = self.json_field(puzzle, 'attempts')
            game['X_Vote'] = self.json_field(puzzle, 'vote')

            # Players
            players = self.json_field(chessgame, 'game/players')
            if not isinstance(players, list):
                return None
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

            # Moves
            moves = self.json_field(chessgame, 'game/treeParts')
            if not isinstance(moves, list):
                return None
            game['_moves'] = ''
            for m in moves:
                if m['ply'] in [0, '0']:
                    game['SetUp'] = '1'
                    game['FEN'] = m['fen']
                else:
                    game['_moves'] += '%s ' % m['san']

            # Solution
            game['_moves'] += ' {Solution: '
            puzzle = self.json_field(puzzle, 'branch')
            while True:
                game['_moves'] += '%s ' % self.json_field(puzzle, 'san')
                puzzle = self.json_field(puzzle, 'children')
                if len(puzzle) == 0:
                    break
                puzzle = puzzle[0]
            game['_moves'] += '}'

            # Rebuild the PGN game
            return self.rebuild_pgn(game)

    def get_test_links(self):
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
                ('https://lichess.org/training/84969', True),                                       # Puzzle
                ('https://lichess.org/training/1281301832', False),                                 # Not a puzzle (wrong ID)
                ('https://lichess.org/broadcast/2019-gct-zagreb-round-4/jQ1dbbX9', True),           # Broadcast
                ('https://lichess.org/broadcast/2019-pychess-round-1/pychess1', False),             # Not a broadcast (wrong ID)
                ('https://lichess.ORG/practice/basic-tactics/the-pin/9ogFv8Ac/BRmScz9t#t', True),   # Practice
                ('https://lichess.org/practice/py/chess/12345678/abcdEFGH', False)]                 # Not a practice (wrong ID)
