# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

from lib.const import CAT_HTML
from lib.cp_interface import InternetGameInterface

import json
from html.parser import HTMLParser
from base64 import b64decode


# ChessBomb.com
class InternetGameChessbomb(InternetGameInterface):
    def get_identity(self):
        return 'ChessBomb.com', CAT_HTML

    def assign_game(self, url):
        return self.reacts_to(url, 'chessbomb.com')

    def download_game(self):
        # Download
        if self.id is None:
            return None
        url = self.id
        page = self.download(url, userAgent=True)  # Else HTTP 403 Forbidden
        if page is None:
            return None

        # Definition of the parser
        class chessbombparser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.last_tag = None
                self.json = None

            def handle_starttag(self, tag, attrs):
                self.last_tag = tag.lower()

            def handle_data(self, data):
                if self.json is None and self.last_tag == 'script':
                    pos1 = data.find('cbConfigData')
                    if pos1 == -1:
                        return
                    pos1 = data.find('"', pos1)
                    pos2 = data.find('"', pos1 + 1)
                    if -1 not in [pos1, pos2]:
                        try:
                            bourne = b64decode(data[pos1 + 1:pos2]).decode().strip()
                            self.json = json.loads(bourne)
                        except Exception:
                            self.json = None
                            return

        # Get the JSON
        parser = chessbombparser()
        parser.feed(page)
        if parser.json is None:
            return None

        # Interpret the JSON
        header = self.json_field(parser.json, 'gameData/game')
        room = self.json_field(parser.json, 'gameData/room')
        moves = self.json_field(parser.json, 'gameData/moves')
        if '' in [header, room, moves]:
            return None

        game = {}
        game['_url'] = url
        game['Event'] = self.json_field(room, 'name')
        game['Site'] = self.json_field(room, 'officialUrl')
        game['Date'] = self.json_field(header, 'startAt')[:10]
        game['Round'] = self.json_field(header, 'roundSlug')
        game['White'] = self.json_field(header, 'white/name')
        game['WhiteElo'] = self.json_field(header, 'white/elo')
        game['Black'] = self.json_field(header, 'black/name')
        game['BlackElo'] = self.json_field(header, 'black/elo')
        game['Result'] = self.json_field(header, 'result')

        game['_moves'] = ''
        for move in moves:
            move = self.json_field(move, 'cbn')
            pos1 = move.find('_')
            if pos1 == -1:
                break
            game['_moves'] += move[pos1 + 1:] + ' '

        # Rebuild the PGN game
        return self.rebuild_pgn(game)

    def get_test_links(self):
        return [('https://www.chessbomb.com/arena/2019-katowice-chess-festival-im/04-Kubicka_Anna-Sliwicka_Alicja', True),          # Game
                ('https://www.chessbomb.com/arena/2019-bangkok-chess-open', False)]                                                 # Not a game (arena)
