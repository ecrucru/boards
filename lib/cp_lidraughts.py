# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_DRAUGHTS, METHOD_DL, TYPE_GAME, TYPE_PUZZLE, TYPE_STUDY
from lib.cp_interface import InternetGameInterface

import re


# Lidraughts.org
class InternetGameLidraughts(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes = {'broadcast': re.compile(r'^https?:\/\/lidraughts\.org\/broadcast\/[a-z0-9\-]+\/([a-z0-9]+)[\/\?\#]?', re.IGNORECASE),
                        'game': re.compile(r'^https?:\/\/lidraughts\.org\/(game\/export\/|embed\/)?([a-z0-9]+)\/?([\S\/]+)?$', re.IGNORECASE),
                        'puzzle': re.compile(r'^https?:\/\/lidraughts\.org\/training\/([0-9]+|daily)[\/\?\#]?', re.IGNORECASE),
                        'study': re.compile(r'^https?:\/\/lidraughts\.org\/study\/([a-z0-9]+(\/[a-z0-9]+)?)(\.pgn)?\/?([\S\/]+)?$', re.IGNORECASE)}

    def get_identity(self):
        return 'Lidraughts.org', BOARD_DRAUGHTS, METHOD_DL

    def assign_game(self, url):
        # Retrieve the ID of the broadcast
        m = self.regexes['broadcast'].match(url)
        if m is not None:
            gid = m.group(1)
            if len(gid) == 8:
                self.url_type = TYPE_STUDY
                self.id = gid
                return True

        # Retrieve the ID of the study
        m = self.regexes['study'].match(url)
        if m is not None:
            gid = m.group(1)
            if len(gid) in [8, 17]:
                self.url_type = TYPE_STUDY
                self.id = gid
                return True

        # Retrieve the ID of the puzzle
        m = self.regexes['puzzle'].match(url)
        if m is not None:
            gid = m.group(1)
            if (gid.isdigit() and gid != '0') or gid == 'daily':
                self.url_type = TYPE_PUZZLE
                self.id = gid
                return True

        # Retrieve the ID of the game
        m = self.regexes['game'].match(url)
        if m is not None:
            gid = m.group(2)
            if len(gid) == 8:
                self.url_type = TYPE_GAME
                self.id = gid
                return True

        # Nothing found
        return False

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Logic for the games
        if self.url_type == TYPE_GAME:
            url = 'https://lidraughts.org/game/export/%s?literate=1' % self.id
            return self.download(url)

        # Logic for the studies
        elif self.url_type == TYPE_STUDY:
            url = 'https://lidraughts.org/study/%s.pdn' % self.id
            return self.download(url, userAgent=True)

        # Logic for the puzzles
        elif self.url_type == TYPE_PUZZLE:
            # Fetch the puzzle
            page = self.download('https://lidraughts.org/training/%s' % self.id)
            if page is None:
                return None

            # Extract the JSON
            page = page.replace("\n", '')
            pos1 = page.find("lidraughts.puzzle =")
            if pos1 == -1:
                return None
            pos1 = page.find('"data"', pos1 + 1)
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
            puzzle = self.json_field(chessgame, 'data/puzzle')
            if puzzle == '':
                return None
            game = {}
            game['_url'] = 'https://lidraughts.org/%s#%s' % (self.json_field(puzzle, 'gameId'), self.json_field(puzzle, 'initialPly'))
            game['Site'] = 'lidraughts.org'
            rating = self.json_field(puzzle, 'rating')
            game['Event'] = 'Puzzle %d, rated %s' % (self.json_field(puzzle, 'id'), rating)
            game['Result'] = '*'
            game['X_Rating'] = rating
            game['X_Attempts'] = self.json_field(puzzle, 'attempts')
            game['X_Vote'] = self.json_field(puzzle, 'vote')

            # Players
            game['White'] = 'White'
            game['Black'] = 'Black'

            # Initial position
            game['SetUp'] = '1'
            game['FEN'] = self.json_field(chessgame, 'data/history/fen')
            game['_moves'] = self.json_field(chessgame, 'data/history/san')

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
        return [('https://lidraughts.org/broadcast/the-big-christmas-show-round-4/JnWAfmOk', True),     # Broadcast
                ('https://lidraughts.org/broadcast/unknown/ABCD1234', False),                           # Broadcast (unknown)
                ('https://LIDRAUGHTS.org/study/3VwAd32E#tag', True),                                    # Study
                ('https://lidraughts.org/study/ABCD1234', False),                                       # Study (unknown)
                ('https://lidraughts.org/study/F88mhTPe/A9uIwROn?arg', True),                           # Chapter of study
                ('https://lidraughts.org/study/F88mhTPe/ABCD1234?arg', True),                           # Chapter of study (unknown but the main study is found)
                ('https://lidraughts.org/study/ABCD1234/abcd1234?arg', False),                          # Chapter of study (both unknown)
                ('https://lidraughts.ORG/RicO2oy8?arg', True),                                          # Game (white side)
                ('https://lidraughts.ORG/RicO2oy8/black', True),                                        # Game (black side)
                ('https://lidraughts.org/training/3620', True),                                         # Puzzle
                ('https://lidraughts.org/training/123456789', True),                                    # Puzzle (unknown)
                ('https://lidraughts.org/about', False),                                                # Not a game (about page)
                ('https://lidraughts.org', False)]                                                      # Not a game (homepage)
