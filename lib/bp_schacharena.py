# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface

import re
from urllib.parse import urlparse, parse_qs
from html import unescape
import chess


# SchachArena.de
class InternetGameSchacharena(InternetGameInterface):
    def __init__(self):
        InternetGameInterface.__init__(self)
        self.regexes.update({'player': re.compile(r'.*spielerstatistik.*name=(\w+).*\[([0-9]+)\].*', re.IGNORECASE),
                             'move': re.compile(r'.*<span.*onMouseOut.*fan\(([0-9]+)\).*', re.IGNORECASE),
                             'result': re.compile(r'.*>(1\-0|0\-1|1\/2\-1\/2)\s([^\<]+)<.*', re.IGNORECASE)})

    def get_identity(self):
        return 'SchachArena.de', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url):
        # Verify the URL
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.schacharena.de', 'schacharena.de'] or 'verlauf' not in parsed.path.lower():
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if 'brett' in args:
            gid = args['brett'][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Download page
        page = self.download('https://www.schacharena.de/new/verlauf.php?brett=%s' % self.id)
        if page is None:
            return None

        # Parse
        player_count = 0
        game = {}
        game['Result'] = '*'
        reason = ''
        game['_moves'] = ''
        game['_url'] = 'https://www.schacharena.de/new/verlauf_to_pgn_n.php?brett=%s' % self.id  # If one want to get the full PGN
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
                game[tag] = m.group(1)
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
                game['Result'] = m.group(1)
                reason = unescape(m.group(2))
                continue

        # Final PGN
        if reason != '':
            game['_moves'] += ' {%s}' % reason
        return self.rebuild_pgn(game)
