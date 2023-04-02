# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021-2022 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, Any, Dict, List, Tuple
from abc import abstractmethod
import logging
import re
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urlencode
from http.client import HTTPResponse

from lib.const import METHOD_WS, BOARD_CHESS, BOARD_DRAUGHTS, BOARD_GO, CHESS960, FEN_START, FEN_START_960


# Abstract class to download a game from the Internet
class InternetGameInterface:
    # Internal
    def __init__(self):
        ''' Initialize the common data that can be used in ALL the sub-classes. '''
        self.reset()
        self.allow_extra = False
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'  # Cloudflare Browser Integrity Check
        self.allow_octet_stream = False
        self.use_sanitization = True
        self.regexes = {'fen': re.compile(r'^[kqbnrp1-8\/]+\s[w|b]\s[kq-]+\s[a-h-][1-8]?(\s[0-9]+)?(\s[0-9]+)?$', re.IGNORECASE),
                        'strip_html': re.compile(r'<\/?[^>]+>', re.IGNORECASE)}

    def reset(self) -> None:
        ''' Clear the internal variables used to fetch the games. '''
        self.id: Optional[str] = None
        self.url_type: Optional[int] = None
        self.data: Optional[str] = None

    def is_enabled(self) -> bool:
        ''' Override this method in the sub-class to disable a chess provider temporarily. '''
        return True

    def get_description(self) -> str:
        ''' Return the description of the board provider. '''
        return self.get_identity()[0]

    def is_async(self) -> bool:
        return self.get_identity()[2] == METHOD_WS

    def get_game_id(self) -> Optional[str]:
        ''' Return the unique identifier of the game that was detected after a successful call to assign_game().
            The value is None if no game was found earlier. '''
        return self.id

    def reacts_to(self, url: Optional[str], host: str) -> bool:
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

    def json_loads(self, data: Optional[str]) -> Optional[Dict]:
        ''' Load a JSON and handle the errors.
            The value None is returned when the data are not relevant or misbuilt. '''
        try:
            if data in [None, '']:
                return None
            return json.loads(str(data))
        except ValueError:
            return None

    def json_field(self,
                   data: Optional[Dict],
                   path: str,
                   default: str = '',
                   separator: str = '/',
                   ) -> str:
        ''' Conveniently read a field from a JSON data. The PATH is a key like "node1/node2/key".
            A blank string is returned in case of error. '''
        if data in [None, '']:
            return ''
        keys = path.split(separator)
        value: Any = data
        for key in keys:
            if key == '*':
                value = list(value.keys())[0]
            elif key.startswith('[') and key.endswith(']'):
                try:
                    value = value[int(key[1:-1])]
                except (ValueError, TypeError, IndexError):
                    return ''
            elif (value is not None) and (key in value):
                value = value[key]
            else:
                return ''
        return default if value in [None, ''] else value

    def read_data(self, response: Optional[HTTPResponse]) -> Optional[str]:
        ''' Read the data from an HTTP request and execute the charset conversion.
            The value None is returned in case of error. '''
        # Check
        if response is None:
            return None
        bdata = response.read()

        # Decode
        cs = response.info().get_content_charset()
        try:
            if cs is not None:
                data = bdata.decode(cs)
            else:
                data = bdata.decode('utf-8')
        except Exception:
            try:
                data = bdata.decode('latin-1')
            except Exception:
                logging.error('Error in the decoding of the data')
                return None

        # Result
        data = data.replace("\ufeff", '').replace("\r", '').strip()
        if data == '':
            return None
        return data

    def expand_links(self, links: List[str], url: str) -> List[str]:
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

    def download(self, url: Optional[str]) -> Optional[str]:
        ''' Download the URL from the Internet.
            The value None is returned in case of error. '''
        # Check
        if url in [None, '']:
            return None

        # Download
        try:
            logging.debug('Downloading game: %s', url)
            headers = {'User-Agent': self.user_agent}
            with urlopen(Request(str(url), headers=headers)) as response:
                data = self.read_data(response)
            return None if data is None or (len(data) == 0) else data
        except Exception as exception:
            logging.debug('Exception raised: %s', str(exception))
            return None

    def download_list(self, links: List[str]) -> Optional[str]:
        ''' Download and concatenate the URL given in the array LINKS.
            The number of downloads is limited to 10.
            The downloads that failed are dropped silently.
            The value None is returned in case of no data or error. '''
        pgn = ''
        for i, link in enumerate(links):
            data = self.download(link)
            if data not in [None, '']:
                pgn += '%s\n\n' % data
            if i >= 10:                             # Anti-flood
                break
        if pgn == '':
            return None
        return pgn

    def send_xhr(self, url: Optional[str], postData: Optional[Dict], origin: Optional[str] = None) -> Optional[str]:
        ''' Call a target URL by submitting the POSTDATA.
            The value None is returned in case of error. '''
        # Check
        if url in [None, '']:
            return None

        # Call data
        if postData is not None:
            data: Optional[bytes] = urlencode(postData).encode()
        else:
            data = None
        try:
            logging.debug('Calling API: %s', url)
            headers = {'User-Agent': self.user_agent,
                       'Accept': 'application/json, text/plain, */*'}
            if origin is not None:
                headers['Origin'] = origin
            with urlopen(Request(str(url), data, headers=headers)) as response:
                respdata = self.read_data(response)
            return respdata
        except Exception as exception:
            logging.debug('Exception raised: %s', str(exception))
            return None

    def rebuild_pgn(self, game: Optional[Dict]) -> Optional[str]:
        ''' Return an object in PGN format.
            The keys starting with "_" are dropped silently.
            The key "_url" becomes the first comment.
            The key "_moves" contains the moves.
            The key "_reason" becomes the last comment. '''
        # Check
        if (game is None) or (game == '') or (game.get('_moves', '') == ''):
            return None

        # Fix the tags
        if 'FEN' in game:                                       # Convert Chess960 to classical chess depending on the start position
            if 'Variant' in game:
                if game['Variant'] == CHESS960 and game['FEN'] == FEN_START_960:
                    del game['Variant'], game['SetUp'], game['FEN']
            else:
                if game['FEN'] == FEN_START:
                    del game['SetUp'], game['FEN']
        if 'Result' in game:                                    # Special signs
            game['Result'] = game['Result'].replace('½', '1/2')

        # Header
        pgn = ''
        roster = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result']
        if 'Player3' in game:                                   # GreenChess
            roster.remove('White')
            roster.remove('Black')
        for tag in roster:
            pgn += '[%s "%s"]\n' % (tag, game.get(tag, '?').strip())
        for e in game:
            if (e not in roster) and (e[:1] != '_') and (game[e] not in [None, '']):
                pgn += '[%s "%s"]\n' % (e, game[e].strip())
        pgn += "\n"

        # Body
        def _inline_tag(key, mask):
            nonlocal pgn
            if key in game and (game[key].strip() != ''):
                pgn += mask % game[key].strip()

        _inline_tag('_url', "{%s}\n")
        _inline_tag('_moves', '%s ')
        _inline_tag('_reason', '{%s} ')
        _inline_tag('Result', '%s ')
        return pgn.strip()

    def sanitize(self, data: Optional[str]) -> Optional[str]:
        ''' Modify the output to comply with the expected format '''
        # Check
        if data in [None, '']:
            return None

        # Reorganize the spaces
        data = str(data).replace('\r', '').strip()
        while True:
            lc = len(data)
            data = data.replace("\n\n\n", "\n\n")
            if len(data) == lc:
                break

        # Game specific rules
        if self.use_sanitization:
            bptype = self.get_identity()[1]
            if bptype == BOARD_CHESS:
                data = data.replace('[Variant "Chess"]\n', '')
            if bptype in [BOARD_CHESS, BOARD_DRAUGHTS]:
                if not data.startswith('['):
                    return None
            if bptype == BOARD_GO:
                if not data.startswith('('):
                    return None

        # Return the data
        return data

    def strip_html(self, html_input: str) -> str:
        ''' Remove any HTML mark from the input parameter. '''
        return self.regexes['strip_html'].sub('', html_input)

    def is_fen(self, fen: Optional[str]) -> bool:
        ''' Test if the argument is a FEN position. '''
        try:
            return self.regexes['fen'].match(fen) is not None
        except TypeError:
            return False

    def seconds2clock(self, seconds: int) -> Tuple[int, int, int]:
        mm, ss = divmod(seconds, 60)
        hh, mm = divmod(mm, 60)
        return (hh, mm, ss)

    # External
    @abstractmethod
    def get_identity(self) -> Tuple[str, int, int]:
        ''' (Abstract) Name and technique of the board provider. '''

    @abstractmethod
    def assign_game(self, url: str) -> bool:
        ''' (Abstract) Detect the unique identifier of URL. '''

    @abstractmethod
    def download_game(self) -> Optional[str]:
        ''' (Abstract) Download the game identified earlier by assign_game(). '''

    @abstractmethod
    def get_test_links(self) -> List[Tuple[str, bool]]:
        ''' (Abstract) Get the links to verify the effectiveness of the download. '''
