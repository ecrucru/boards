# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from lib.const import BOARD_CHESS, METHOD_HTML, TYPE_GAME, TYPE_PUZZLE
from lib.bp_interface import InternetGameInterface

from urllib.parse import urlparse, parse_qs, unquote
import chess


# GameKnot.com
class InternetGameGameknot(InternetGameInterface):
    def get_identity(self):
        return 'GameKnot.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url):
        # Verify the hostname
        parsed = urlparse(url.lower())
        if parsed.netloc not in ['www.gameknot.com', 'gameknot.com']:
            return False

        # Verify the page
        if parsed.path == '/analyze-board.pl':
            ttype = TYPE_GAME
            tkey = 'bd'
        elif parsed.path == '/chess-puzzle.pl':
            ttype = TYPE_PUZZLE
            tkey = 'pz'
        else:
            return False

        # Read the arguments
        args = parse_qs(parsed.query)
        if tkey in args:
            gid = args[tkey][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                self.url_type = ttype
                return True
        return False

    def download_game(self):
        # Check
        if self.url_type not in [TYPE_GAME, TYPE_PUZZLE] or self.id is None:
            return None

        # Download
        if self.url_type == TYPE_GAME:
            url = 'https://gameknot.com/analyze-board.pl?bd=%s' % self.id
        elif self.url_type == TYPE_PUZZLE:
            url = 'https://gameknot.com/chess-puzzle.pl?pz=%s' % self.id
        page = self.download(url, userAgent=True)
        if page is None:
            return None

        # Library
        def extract_variables(page, structure):
            game = {}
            for var, type, tag in structure:
                game[tag] = ''
            lines = page.split(';')
            for line in lines:
                for var, type, tag in structure:
                    pos1 = line.find(var)
                    if pos1 == -1:
                        continue
                    if type == 's':
                        pos1 = line.find("'", pos1 + 1)
                        pos2 = line.find("'", pos1 + 1)
                        if pos2 > pos1:
                            game[tag] = line[pos1 + 1:pos2]
                    elif type == 'i':
                        pos1 = line.find('=', pos1 + 1)
                        if pos1 != -1:
                            txt = line[pos1 + 1:].strip()
                            if txt not in ['', '0']:
                                game[tag] = txt
                    else:
                        assert(False)
            return game

        # Logic for the puzzles
        if self.url_type == TYPE_PUZZLE:
            structure = [('puzzle_id', 'i', '_id'),
                         ('puzzle_fen', 's', 'FEN'),
                         ('load_solution(', 's', '_solution')]
            game = extract_variables(page, structure)
            game['_url'] = 'https://gameknot.com/chess-puzzle.pl?pz=%s' % game['_id']
            game['White'] = 'White'
            game['Black'] = 'Black'
            game['Result'] = '*'
            if game['FEN'] != '':
                game['SetUp'] = '1'
            if game['_solution'] != '':
                list = game['_solution'].split('|')
                game['_moves'] = ' {Solution:'
                nextid = '0'
                for item in list:
                    item = item.split(',')
                    # 0 = identifier of the move
                    # 1 = player
                    # 2 = identifier of the previous move
                    # 3 = count of following moves
                    # 4 = algebraic notation of the move
                    # 5 = UCI notation of the move
                    # 6 = ?
                    # 7 = identifier of the next move
                    # > = additional moves for the current line
                    curid = item[0]
                    if curid != nextid:
                        continue
                    if len(item) == 4:
                        break
                    nextid = item[7]
                    move = item[4]  # No AN is 5
                    game['_moves'] += ' %s' % move
                game['_moves'] += '}'

        # Logic for the games
        elif self.url_type == TYPE_GAME:
            # Header
            structure = [('anbd_movelist', 's', '_moves'),
                         ('anbd_result', 'i', 'Result'),
                         ('anbd_player_w', 's', 'White'),
                         ('anbd_player_b', 's', 'Black'),
                         ('anbd_rating_w', 'i', 'WhiteElo'),
                         ('anbd_rating_b', 'i', 'BlackElo'),
                         ('anbd_title', 's', 'Event'),
                         ('anbd_timestamp', 's', 'Date'),
                         ('export_web_input_result_text', 's', '_reason')]
            game = extract_variables(page, structure)
            if game['Result'] == '1':
                game['Result'] = '1-0'
            elif game['Result'] == '2':
                game['Result'] = '1/2-1/2'
            elif game['Result'] == '3':
                game['Result'] = '0-1'
            else:
                game['Result'] = '*'

            # Body
            board = chess.Board()
            moves = game['_moves'].split('-')
            game['_moves'] = ''
            for move in moves:
                if move == '':
                    break
                try:
                    kmove = chess.Move.from_uci(move)
                    game['_moves'] += board.san(kmove) + ' '
                    board.push(kmove)
                except Exception:
                    return None

        # Rebuild the PGN game
        return unquote(self.rebuild_pgn(game))

    def get_test_links(self):
        return [('https://gameknot.com/analyze-board.pl?bd=22792465#tag', True),        # Game
                ('https://GAMEKNOT.com/chess.pl?bd=22792465&p=1', False),               # Not a game (wrong path)
                ('https://gameknot.com/analyze-board.pl?bd=1234567890&p=1', False),     # Not a game (unknown ID)
                ('https://gameknot.com/analyze-board.pl?bd=bepofr#tag', False),         # Not a game (not numeric ID)
                ('https://gameknot.com', False),                                        # Not a game (homepage)
                ('https://gameknot.com/chess-puzzle.pl?pz=224260', True),               # Puzzle
                ('https://gameknot.com/chess-puzzle.pl?pz=224541&next=2', True),        # Puzzle with parameters
                ('https://gameknot.com/chess-puzzle.pl?pz=224571', True),               # Puzzle with analysis
                ('https://gameknot.com/chess-puzzle.pl?pz=ABC', False),                 # Random puzzle but rejected by PyChess (wrong format)
                ('https://gameknot.com/chess-puzzle.pl?pz=0#tag', False)]               # Random puzzle but rejected by PyChess (wrong format)
