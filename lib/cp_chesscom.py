# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_MISC, CHESS960, TYPE_FEN
from lib.cp_interface import InternetGameInterface

import re
from urllib.parse import urlparse, parse_qs
from html.parser import HTMLParser
import chess


# Chess.com
class InternetGameChessCom(InternetGameInterface):
    def get_identity(self):
        return 'Chess.com', CAT_MISC

    def assign_game(self, url):
        # Positions
        parsed = urlparse(url)
        if parsed.netloc.lower() in ['www.chess.com', 'chess.com']:
            args = parse_qs(parsed.query)
            if 'fen' in args:
                fen = args['fen'][0]
                if self.is_fen(fen):
                    self.url_type = TYPE_FEN
                    self.id = fen
                    return True

        # Puzzles
        rxp = re.compile(r'^https?:\/\/(\S+\.)?chess\.com\/([a-z\/]+)?(puzzles)\/problem\/([0-9]+)[\/\?\#]?', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            self.url_type = m.group(3).lower()
            self.id = m.group(4)
            return True

        # Games
        url = url.replace('/live#g=', '/live/game/').replace('/daily#g=', '/daily/game/')
        rxp = re.compile(r'^https?:\/\/(\S+\.)?chess\.com\/([a-z\/]+)?(live|daily)\/([a-z\/]+)?([0-9]+)[\/\?\#]?', re.IGNORECASE)
        m = rxp.match(url)
        if m is not None:
            self.url_type = m.group(3).lower()
            self.id = m.group(5)
            return True
        return False

    def decode_move(self, move):
        # Mapping
        map = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?{~}(^)[_]@#$,./&-*++='
        pieces = 'qnrbkp'

        # Analyze the move
        sFrom = sTo = sPromo = sDrop = ''
        posFrom = map.index(move[:1])
        posTo = map.index(move[1:])
        if posTo > 63:
            sPromo = pieces[(posTo - 64) // 3]
            posTo = posFrom + (-8 if posFrom < 16 else 8) + (posTo - 1) % 3 - 1
        if posFrom > 75:
            sDrop = pieces[posFrom - 79].upper() + '@'
        else:
            sFrom = map[posFrom % 8] + str((posFrom // 8 + 1))
        sTo = map[posTo % 8] + str((posTo // 8 + 1))
        return '%s%s%s%s' % (sDrop, sFrom, sTo, sPromo)

    def download_game(self):
        # Check
        if None in [self.id, self.url_type]:
            return None

        # Positions
        if self.url_type == TYPE_FEN:
            return '[Site "chess.com"]\n[White "%s"]\n[Black "%s"]\n[SetUp "1"]\n[FEN "%s"]\n\n*' % ('White', 'Black', self.id)

        # Puzzles
        elif self.url_type == 'puzzles':
            url = 'https://www.chess.com/puzzles/problem/%s' % self.id
            page = self.download(url, userAgent=True)  # Else 403 Forbidden
            if page is None:
                return None

            # Definition of the parser
            class chesscomparser(HTMLParser):
                def __init__(self):
                    HTMLParser.__init__(self)
                    self.pgn = None

                def handle_starttag(self, tag, attrs):
                    if tag.lower() == 'div':
                        for k, v in attrs:
                            if k.lower() == 'data-puzzle':
                                self.pgn = v.replace('&quote;', '"').replace('\\/', '/')

            # Parse the page
            parser = chesscomparser()
            parser.feed(page)
            if parser.pgn is None:
                return None

            # Load the JSON
            puzzle = self.json_loads(parser.pgn)
            if puzzle in [None, '']:
                return None

            # Get the game directly if available
            pgn = self.json_field(puzzle, 'pgn')
            if pgn != '':
                pgn = pgn.replace('\\n', '\n')
                pgn = pgn.replace('\\"', '"')
                pgn = pgn.replace('     ', ' ')
                pgn = pgn.replace('. ...', '...')
                pgn = pgn.replace('\\t', '    ')
                return pgn

            # Rebuild the puzzle
            game = {}
            game['_url'] = url
            refid = self.json_field(puzzle, 'gameLiveId')
            if refid not in [None, 0, '']:
                game['_url'] = 'https://www.chess.com/live/game/%d' % refid
            else:
                refid = self.json_field(puzzle, 'gameId')
                if refid not in [None, 0, '']:
                    game['_url'] = 'https://www.chess.com/daily/game/%d' % refid
            rating = self.json_field(puzzle, 'rating')
            game['Event'] = 'Puzzle %s, rated %s' % (str(self.json_field(puzzle, 'id')), rating)
            game['White'] = 'White'
            game['Black'] = 'Black'
            game['Result'] = '*'
            game['TimeControl'] = '%d+0' % self.json_field(puzzle, 'averageSeconds')
            game['FEN'] = self.json_field(puzzle, 'initialFen')
            game['SetUp'] = '1'
            game['X_ID'] = self.json_field(puzzle, 'id')
            game['X_Rating'] = rating
            game['X_Attempts'] = self.json_field(puzzle, 'attemptCount')
            game['X_PassRate'] = self.json_field(puzzle, 'passRate')
            buffer = '{%s}' % self.json_field(puzzle, 'internalNote').strip()
            if buffer == '{}':
                buffer = '{The first move is not provided}'
            game['_moves'] = buffer

        # Games
        else:
            # API since October 2020
            url = 'https://www.chess.com/callback/%s/game/%s' % (self.url_type, self.id)
            bourne = self.send_xhr(url, {}, userAgent=True)
            if bourne is None:
                return None

            # Read the JSON
            chessgame = self.json_loads(bourne)
            if not self.allow_extra and self.json_field(chessgame, 'game/isRated') and not self.json_field(chessgame, 'game/isFinished'):
                return None
            chessgame = self.json_field(chessgame, 'game')
            if chessgame == '':
                return None

            # Header
            headers = self.json_field(chessgame, 'pgnHeaders')
            if headers == '':
                game = {}
            else:
                game = headers
            if 'Variant' in game and game['Variant'] == 'Chess960':
                game['Variant'] = CHESS960
            game['_url'] = url.replace('/callback/', '/')

            # Body
            moves = self.json_field(chessgame, 'moveList')
            if moves == '':
                return None
            game['_moves'] = ''
            if 'Variant' in game and game['Variant'] == 'Crazyhouse':
                board = chess.variant.CrazyhouseBoard()
            else:
                board = chess.Board(chess960=True)
            if 'FEN' in game:
                board.set_fen(game['FEN'])
            while len(moves) > 0:
                move = self.decode_move(moves[:2])
                moves = moves[2:]
                try:
                    if self.use_an:
                        kmove = chess.Move.from_uci(move)
                        game['_moves'] += board.san(kmove) + ' '
                        board.push(kmove)
                    else:
                        game['_moves'] += move + ' '
                except Exception:
                    return None

        # Final PGN
        return self.rebuild_pgn(game)
