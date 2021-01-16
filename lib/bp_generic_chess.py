# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from urllib.request import Request, urlopen
from urllib.parse import urlparse
from html.parser import HTMLParser

from lib.const import BOARD_CHESS, METHOD_MISC
from lib.bp_interface import InternetGameInterface


# Generic
class InternetGameGenericChess(InternetGameInterface):
    def get_identity(self):
        return 'Generic for chess', BOARD_CHESS, METHOD_MISC

    def assign_game(self, url):
        # Any page is valid
        self.id = url
        return True

    def download_game(self):
        # Check
        if self.id is None:
            return None

        # Download
        req = Request(self.id, headers={'User-Agent': self.userAgent})
        response = urlopen(req)
        mime = response.info().get_content_type().lower()
        data = self.read_data(response)
        if data is None:
            return None

        # Chess file
        if (mime in ['application/x-chess-pgn', 'application/pgn']) or (self.allow_octet_stream and mime == 'application/octet-stream'):
            return data

        # Web-page
        if mime == 'text/html':
            # Definition of the parser
            class linksParser(HTMLParser):
                def __init__(self):
                    HTMLParser.__init__(self)
                    self.links = []

                def handle_starttag(self, tag, attrs):
                    if tag.lower() == 'a':
                        for k, v in attrs:
                            if k.lower() == 'href':
                                v = v.strip()
                                u = urlparse(v)
                                if u.path.lower().endswith('.pgn'):
                                    self.links.append(v)

            # Read the links
            parser = linksParser()
            parser.feed(data)
            parser.links = self.expand_links(parser.links, self.id)
            return self.download_list(parser.links)
        return None

    def get_test_links(self):
        return [('https://thechessworld.com/pgngames/middlegames/sacrifice-on-e6/Ivanchuk-Karjakin.pgn', True)]     # Game with UTF-8 BOM
