# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3


# Libraries
import argparse
import asyncio
import logging
import re
from urllib.parse import urlparse
from random import choice

# Highest priority
from lib.cp_lichess import InternetGameLichess
from lib.cp_chesscom import InternetGameChessCom
from lib.cp_chess24 import InternetGameChess24
# Normal priority
from lib.cp_interface import InternetGameInterface
from lib.cp_2700chess import InternetGame2700chess
from lib.cp_365chess import InternetGame365chess
from lib.cp_chessbase import InternetGameChessbase
from lib.cp_chessbomb import InternetGameChessbomb
from lib.cp_chessdb import InternetGameChessdb
from lib.cp_chessgames import InternetGameChessgames
from lib.cp_chessking import InternetGameChessking
from lib.cp_chessorg import InternetGameChessOrg
from lib.cp_chesspastebin import InternetGameChesspastebin
from lib.cp_chesspro import InternetGameChesspro
from lib.cp_chesspuzzle import InternetGameChesspuzzle
from lib.cp_chesssamara import InternetGameChesssamara
from lib.cp_chesstempo import InternetGameChesstempo
from lib.cp_europeechecs import InternetGameEuropeechecs
from lib.cp_ficgs import InternetGameFicgs
from lib.cp_ficsgames import InternetGameFicsgames
from lib.cp_gameknot import InternetGameGameknot
from lib.cp_iccf import InternetGameIccf
from lib.cp_ideachess import InternetGameIdeachess
from lib.cp_playok import InternetGamePlayok
from lib.cp_pychess import InternetGamePychess
from lib.cp_redhotpawn import InternetGameRedhotpawn
from lib.cp_schacharena import InternetGameSchacharena
from lib.cp_schachspielen import InternetGameSchachspielen
from lib.cp_thechessworld import InternetGameThechessworld
# Lowest priority
from lib.cp_generic import InternetGameGeneric

chess_providers = []


# Retrieve a game from a URL
async def download(url):
    # Recognize the most popular identifiers
    if url in [None, '']:
        return None
    if re.compile(r'^[a-z0-9-]{8}$', re.IGNORECASE).match(url) is not None:
        url = 'https://lichess.org/' + url
    elif re.compile(r'^[a-z0-9]{5}$', re.IGNORECASE).match(url) is not None:
        url = 'https://lichess.org/training/' + url
    elif url.isdigit():
        url = 'https://www.chess.com/live/game/' + url

    # Check the format
    p = urlparse(url.strip())
    if '' in [p.scheme, p.netloc]:
        return None
    logging.debug('URL to retrieve: %s' % url)

    # Call the chess providers
    for prov in chess_providers:
        if not prov.is_enabled():
            continue
        prov.reset()
        if prov.assign_game(url):
            # Download
            logging.debug('Responding chess provider: %s' % prov.get_description())
            try:
                if prov.is_async():
                    pgn = await prov.download_game()
                else:
                    pgn = prov.download_game()
                pgn = prov.sanitize(pgn)
            except Exception as e:
                pgn = None
                logging.debug(str(e))

            # Check
            if pgn is None:
                logging.debug('Download failed')
            else:
                logging.debug('Successful download')
                return pgn
    return None


# Start of the program
async def main():
    # Load the chess providers from the imported classes
    global chess_providers
    for cls in InternetGameInterface.__subclasses__():
        chess_providers.append(cls())

    # Command line
    parser = argparse.ArgumentParser(prog='python chessdl.py', description='chess-dl is a download helper for the chess games')
    subparser = parser.add_subparsers(dest='command')

    subparser.add_parser('show', help='Show the supported chess providers')

    group = subparser.add_parser('download', help='Download a game')
    group.add_argument('url', default='', help='URL of the chess game')
    group.add_argument('--unverified-ssl', action='store_true', help='Use an unverified SSL context to avoid some errors with SSL')

    subparser.add_parser('test', help='Run the quality test')

    # Execute
    parser = parser.parse_args()
    if parser.command == 'show':
        list = [cp.get_description() for cp in chess_providers if cp.is_enabled()]
        list.sort()
        [print(cp) for cp in list]

    elif parser.command == 'download':
        if parser.unverified_ssl:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
        print(await download(parser.url))

    elif parser.command == 'test':
        for cp in chess_providers:
            # Check
            if cp is None:
                continue
            logging.info("\n%s" % cp.get_description())
            links = cp.get_test_links()
            if len(links) == 0:
                logging.info('- No available test link')
                continue
            if not cp.is_enabled():
                logging.info('- Disabled module')
                continue

            # Pick one link only to not overload the remote server
            url, expected = choice(links)
            logging.info('- Target link: %s' % url)
            logging.info('- Expecting data: %s' % expected)

            # Download link
            cp.reset()
            if not cp.assign_game(url):
                data = None
            else:
                try:
                    data = cp.download_game()
                    data = cp.sanitize(data)
                except Exception:
                    logging.debug(str(Exception))
                    data = None

            # Result
            ok = data is not None
            logging.info('- Fetched data: %s' % ok)
            if ok:
                logging.info(data)
            if ok != expected:
                logging.error('- Test in error')

    else:
        assert(False)


asyncio.run(main())
