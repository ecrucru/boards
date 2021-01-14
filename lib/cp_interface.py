# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

import logging
import os
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urlencode

from lib.ua import InternetUserAgent
from lib.const import ANNOTATOR, CAT_WS, CHESS960, FEN_START, FEN_START_960, REGEX_FEN, REGEX_STRIP_HTML


# Abstract class to download a game from the Internet
class InternetGameInterface:
    # Internal
    def __init__(self):
        ''' Initialize the common data that can be used in ALL the sub-classes. '''
        self.reset()
        self.ua = InternetUserAgent()
        self.allow_extra = False
        self.userAgent = self.ua.generate(fake=self.allow_extra)
        self.use_an = True  # To rebuild a readable PGN where possible
        self.allow_octet_stream = False

    def reset(self):
        ''' Clear the internal variables used to fetch the games. '''
        self.id = None
        self.url_type = None
        self.data = None

    def is_enabled(self):
        ''' Override this method in the sub-class to disable a chess provider temporarily. '''
        return True

    def get_description(self):
        ''' Return the description of the chess provider. '''
        return self.get_identity()[0]

    def is_async(self):
        return self.get_identity()[1] == CAT_WS

    def get_game_id(self):
        ''' Return the unique identifier of the game that was detected after a successful call to assign_game().
            The value is None if no game was found earlier. '''
        return self.id

    def reacts_to(self, url, host):
        ''' Return True if the URL belongs to the HOST (possibly equal to *). The sub-domains other than "www" are not supported.
            The method is used to accept any URL when a unique identifier cannot be extracted by assign_game(). '''
        # Verify the hostname
        if url is None:
            return False
        if host != '*':
            parsed = urlparse(url)
            if parsed.netloc.lower() not in ['www.' + host.lower(), host.lower()]:
                return False

        # Any page is valid
        self.id = url
        return True

    def json_loads(self, data):
        ''' Load a JSON and handle the errors.
            The value None is returned when the data are not relevant or misbuilt. '''
        try:
            if data in [None, '']:
                return None
            return json.loads(data)
        except ValueError:
            return None

    def json_field(self, data, path, default=''):
        ''' Conveniently read a field from a JSON data. The PATH is a key like "node1/node2/key".
            A blank string is returned in case of error. '''
        if data in [None, '']:
            return ''
        keys = path.split('/')
        value = data
        for key in keys:
            if key.startswith('[') and key.endswith(']'):
                try:
                    value = value[int(key[1:-1])]
                except (ValueError, TypeError, IndexError):
                    return ''
            else:
                if key in value:
                    value = value[key]
                else:
                    return ''
        return default if value in [None, ''] else value

    def read_data(self, response):
        ''' Read the data from an HTTP request and execute the charset conversion.
            The value None is returned in case of error. '''
        # Check
        if response is None:
            return None
        bytes = response.read()

        # Decode
        cs = response.info().get_content_charset()
        if cs is not None:
            data = bytes.decode(cs)
        else:
            try:
                data = bytes.decode('utf-8')
            except Exception:
                try:
                    data = bytes.decode('latin-1')
                except Exception:
                    logging.debug('Error in the decoding of the data')
                    return None

        # Result
        data = data.replace("\ufeff", '').replace("\r", '').strip()
        if data == '':
            return None
        else:
            return data

    def expand_links(self, links, url):
        ''' Convert relative paths into full paths. '''
        base = urlparse(url)
        for i, link in enumerate(links):
            e = urlparse(link)
            if e.netloc == '':
                if e.path.startswith('/'):
                    link = '%s://%s%s' % (base.scheme, base.netloc, e.path)
                else:
                    link = '%s://%s%s/%s' % (base.scheme, base.netloc, '/'.join(base.path.split('/')[:-1]), e.path)
            links[i] = link
        return list(dict.fromkeys(links))       # Without duplicate entries

    def download(self, url, userAgent=False):
        ''' Download the URL from the Internet.
            The USERAGENT is requested by some websites to make sure that you are not a bot.
            The value None is returned in case of error. '''
        # Check
        if url in [None, '']:
            return None

        # Download
        try:
            logging.debug('Downloading game: %s' % url)
            if userAgent:
                req = Request(url, headers={'User-Agent': self.userAgent})
                response = urlopen(req)
            else:
                response = urlopen(url)
            return self.read_data(response)
        except Exception as exception:
            logging.debug('Exception raised: %s' % str(exception))
            return None

    def download_list(self, links, userAgent=False):
        ''' Download and concatenate the URL given in the array LINKS.
            The USERAGENT is requested by some websites to make sure that you are not a bot.
            The number of downloads is limited to 10.
            The downloads that failed are dropped silently.
            The value None is returned in case of no data or error. '''
        pgn = ''
        for i, link in enumerate(links):
            data = self.download(link, userAgent)
            if data not in [None, '']:
                pgn += '%s\n\n' % data
            if i >= 10:                             # Anti-flood
                break
        if pgn == '':
            return None
        else:
            return pgn

    def send_xhr(self, url, postData, userAgent=False):
        ''' Call a target URL by submitting the POSTDATA.
            The USERAGENT is requested by some websites to make sure that you are not a bot.
            The value None is returned in case of error. '''
        # Check
        if url in [None, ''] or postData in [None, '']:
            return None

        # Call data
        try:
            logging.debug('Calling API: %s' % url)
            if userAgent:
                req = Request(url, urlencode(postData).encode(), headers={'User-Agent': self.userAgent})
            else:
                req = Request(url, urlencode(postData).encode())
            response = urlopen(req)
            return self.read_data(response)
        except Exception as exception:
            logging.debug('Exception raised: %s' % str(exception))
            return None

    def rebuild_pgn(self, game):
        ''' Return an object in PGN format.
            The keys starting with "_" are dropped silently.
            The key "_url" becomes the first comment.
            The key "_moves" contains the moves.
            The key "_reason" becomes the last comment. '''
        # Check
        if game is None or game == '' or '_moves' not in game or game['_moves'] == '':
            return None

        # Convert Chess960 to classical chess depending on the start position
        if 'FEN' in game:
            if 'Variant' in game:
                if game['Variant'] == CHESS960 and game['FEN'] == FEN_START_960:
                    del game['Variant'], game['SetUp'], game['FEN']
            else:
                if game['FEN'] == FEN_START:
                    del game['SetUp'], game['FEN']

        # Header
        pgn = ''
        for e in game:
            if e[:1] != '_' and game[e] not in [None, '']:
                pgn += '[%s "%s"]\n' % (e, game[e])
        if pgn == '':
            pgn = '[Annotator "%s"]\n' % ANNOTATOR
        pgn += "\n"

        # Body
        if '_url' in game:
            pgn += "{%s}\n" % game['_url']
        if '_moves' in game:
            pgn += '%s ' % game['_moves']
        if '_reason' in game:
            pgn += '{%s} ' % game['_reason']
        if 'Result' in game:
            pgn += '%s ' % game['Result']
        return pgn.strip()

    def sanitize(self, pgn):
        ''' Modify the PGN output to comply with the expected format '''
        # Check
        if pgn in [None, '']:
            return None

        # Verify that it starts with the correct magic character (ex.: "<" denotes an HTML content, "[" a chess game, etc...)
        pgn = pgn.replace('\r', '').strip()
        if not pgn.startswith('['):
            return None

        # Reorganize the spaces to bypass Scoutfish's limitation
        while (True):
            lc = len(pgn)
            pgn = pgn.replace("\n\n\n", "\n\n")
            if len(pgn) == lc:
                break

        # Variants
        pgn = pgn.replace('[Variant "Chess"]\n', '')

        # Return the PGN with the local crlf
        return pgn.replace("\n", os.linesep)

    def strip_html(self, input):
        ''' Remove any HTML mark from the input parameter. '''
        return REGEX_STRIP_HTML.sub('', input)

    def is_fen(self, fen):
        ''' Test if the argument is a FEN position. '''
        try:
            return REGEX_FEN.match(fen) is not None
        except TypeError:
            return False

    # External
    def get_identity(self):
        ''' (Abstract) Name and technique of the chess provider. '''
        pass

    def assign_game(self, url):
        ''' (Abstract) Detect the unique identifier of URL. '''
        pass

    def download_game(self):
        ''' (Abstract) Download the game identified earlier by assign_game(). '''
        pass

    def get_test_links(self):
        ''' (Abstract) Get the links to verify the effectiveness of the download. '''
        return []
