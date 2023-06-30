# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from html import unescape
from urllib.parse import urlparse, parse_qs

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# GreenChess.net
class InternetGameGreenchess(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'GreenChess.net', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        # Verify the host
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ['www.greenchess.net', 'greenchess.net']:
            return False

        # Read the identifier
        args = parse_qs(parsed.query)
        if 'id' in args:
            gid = args['id'][0]
            if gid.isdigit() and gid != '0':
                self.id = gid
                return True
        return False

    def download_game(self) -> Optional[str]:
        # Download the page
        if self.id is None:
            return None
        url = 'https://greenchess.net/game.php?id=%s' % self.id
        page = self.download(url)
        if page is None:
            return None
        game = {}
        game['Site'] = url

        # Simplify the page
        page = (unescape(page.replace('&nbsp;', ' '))
                .replace('\r', '')
                .replace("<img src='icon/pawn-white.png' class='color-icon'/>", '')
                .replace("<img src='icon\\/pawn-white.png' class='color-icon'\\/>", '')
                .replace("<img src='icon/pawn-black.png' class='color-icon'/>", '')
                .replace("<img src='icon\\/pawn-black.png' class='color-icon'\\/>", '')
                .replace("<img src='icon/pawn-red.png' class='color-icon'/>", '')
                .replace("<img src='icon\\/pawn-red.png' class='color-icon'\\/>", '')
                .replace("<img src='icon/wire-rook.png' alt='Rook' class='piece-icon'/>", 'R')
                .replace("<img src='icon/wire-rook4.png' alt='Short rook' class='piece-icon'/>", 'R')
                .replace("<img src='icon/wire-bishop.png' alt='Bishop' class='piece-icon'/>", 'B')
                .replace("<img src='icon/wire-knight.png' alt='Knight' class='piece-icon'/>", 'N')
                .replace("<img src='icon/wire-queen.png' alt='Queen' class='piece-icon'/>", 'Q')
                .replace("<img src='icon/wire-king.png' alt='King' class='piece-icon'/>", 'K')
                .replace("<img src='icon/wire-archbis.png' alt='Archbishop' class='piece-icon'/>", 'A')         # A = B + N
                .replace("<img src='icon/wire-amazon.png' alt='Superqueen' class='piece-icon'/>", 'Z')          # Z* = Q + N
                .replace("<img src='icon/wire-chancel.png' alt='Chancellor' class='piece-icon'/>", 'C')         # C = R + N
                .replace("<img src='icon/wire-centaur.png' alt='Centaur' class='piece-icon'/>", 'M')            # M = N + K
                .replace("<img src='icon/wire-nightrd.png' alt='Nightrider' class='piece-icon'/>", 'N')         # N = N + N + ...
                .replace("<img src='icon/wire-grassh.png' alt='Grasshopper' class='piece-icon'/>", 'G')         # G* = jumps behind
                .replace("<img src='icon/wire-augnf.png' alt='Augmented knight' class='piece-icon'/>", 'N')
                .replace('<div', '\n<div')
                .replace('</div>', '')
                .replace('> ', '>')
                .replace(' 0-0-0', ' O-O-O')
                .replace(' 0-0', ' O-O'))

        # Parse the moves
        moves: List[str] = []
        for line in page.split('\n'):
            if ("class='history-item'" not in line) or ('Start' in line):
                continue
            moves.insert(0, line.split(' ')[-1])
        if len(moves) == 0:
            return None
        game['_moves'] = ' '.join(moves)

        # Data of the header
        # ... variant
        p1 = page.find('<title>')
        p2 = page.find('</title>', p1)
        game['Event'] = page[p1 + 7:p2].strip()
        p1 = game['Event'].find(' – ')              # &ndash;
        game['Variant'] = game['Event'][:p1]
        # Reduction
        pos = page.find('uweb-commands')
        if pos == -1:
            return None
        page = page[pos:]
        # ... players
        names = []
        for i in range(3):
            p1 = page.find('"player-%d":' % i)
            if p1 == -1:
                break
            p1 = page.find('"text":"', p1)
            p1 += 8
            p2 = page.find('"', p1)
            if p2 > p1:
                names.append(page[p1:p2])
        if len(names) == 2:
            game['White'] = names[0]
            game['Black'] = names[1]
        else:
            for i, name in enumerate(names):
                game['Player%d' % (i + 1)] = name
        # ... score
        if len(names) == 2:
            if page.find("'draw'") != -1:
                game['Result'] = '1/2-1/2'
            elif page.find("'winner'") > page.find("'loser'"):
                game['Result'] = '0-1'
            else:
                game['Result'] = '1-0'

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://greenchess.net/game.php?id=6923', True),      # Game
                ('https://greenchess.net/game.php?id=8733', True),      # Game (draw)
                ('https://greenchess.net/game.php?id=1001', True),      # Game (fairy piece)
                ('https://greenchess.net/game.php?id=88352', True),     # Game (3 players)
                ('https://greenchess.net/game.php?id=abc123', False),   # Not a game (wrong id)
                ('https://greenchess.net', False),                      # Not a game (homepage)
                ]
