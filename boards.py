# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3


# Libraries
import argparse
import asyncio
import logging
import sys
import re
from urllib.parse import urlparse
from random import choice

from lib.const import BOARD_CHESS, BOARD_DRAUGHTS, BOARD_GO

# Popular chess
from lib.bp_lichess import InternetGameLichess
from lib.bp_chesscom import InternetGameChessCom
from lib.bp_chess24 import InternetGameChess24
# Normal chess
from lib.bp_interface import InternetGameInterface
from lib.bp_2700chess import InternetGame2700chess
from lib.bp_365chess import InternetGame365chess
from lib.bp_chessbase import InternetGameChessbase
from lib.bp_chessbomb import InternetGameChessbomb
from lib.bp_chessdb import InternetGameChessdb
from lib.bp_chessgames import InternetGameChessgames
from lib.bp_chessking import InternetGameChessking
from lib.bp_chessorg import InternetGameChessOrg
from lib.bp_chesspastebin import InternetGameChesspastebin
from lib.bp_chesspro import InternetGameChesspro
from lib.bp_chesspuzzle import InternetGameChesspuzzle
from lib.bp_chesssamara import InternetGameChesssamara
from lib.bp_chesstempo import InternetGameChesstempo
from lib.bp_europeechecs import InternetGameEuropeechecs
from lib.bp_ficgs import InternetGameFicgs
from lib.bp_ficsgames import InternetGameFicsgames
from lib.bp_gameknot import InternetGameGameknot
from lib.bp_iccf import InternetGameIccf
from lib.bp_ideachess import InternetGameIdeachess
from lib.bp_mskchess import InternetGameMskchess
from lib.bp_playok import InternetGamePlayok
from lib.bp_pychess import InternetGamePychess
from lib.bp_redhotpawn import InternetGameRedhotpawn
from lib.bp_schacharena import InternetGameSchacharena
from lib.bp_schachspielen import InternetGameSchachspielen
from lib.bp_thechessworld import InternetGameThechessworld
# Draughts
from lib.bp_lidraughts import InternetGameLidraughts
# Go
from lib.bp_dragongoserver import InternetGameDragongoserver
from lib.bp_gokgs import InternetGameGokgs
from lib.bp_goshrine import InternetGameGoshrine
from lib.bp_onlinego import InternetGameOnlinego
# Lowest priority
from lib.bp_generic_chess import InternetGameGenericChess

board_providers = []


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

    # Call the board providers
    for prov in board_providers:
        if not prov.is_enabled():
            continue
        prov.reset()
        if prov.assign_game(url):
            # Download
            logging.debug('Responding board provider: %s' % prov.get_description())
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
    # Load the board providers from the imported classes
    global board_providers
    for cls in InternetGameInterface.__subclasses__():
        board_providers.append(cls())

    # Command line
    cmdline = argparse.ArgumentParser(prog='python boards.py', description='Boards is a download helper for the online board games (chess, draughts, go...)')
    subparser = cmdline.add_subparsers(dest='command')

    subparser.add_parser('show', help='Show the supported board providers')

    group = subparser.add_parser('download', help='Download a game')
    group.add_argument('url', default='', help='URL of the board game')
    group.add_argument('--unverified-ssl', action='store_true', help='Use an unverified SSL context to avoid some errors with SSL')

    subparser.add_parser('test', help='Run the quality test')

    # Execute
    parser = cmdline.parse_args()
    if parser.command == 'show':
        method_desc = {BOARD_CHESS: 'Chess',
                       BOARD_DRAUGHTS: 'Draughts',
                       BOARD_GO: 'Go'}
        list = []
        for bp in board_providers:
            if bp.is_enabled():
                site, board, method = bp.get_identity()
                list.append('%s - %s' % (method_desc[board], site))
        list.sort()
        [print(bp) for bp in list]

    elif parser.command == 'download':
        # SSL
        if parser.unverified_ssl:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

        # Download
        data = await download(parser.url)
        if data is not None:
            print(data)
        else:
            logging.error('No game found.')

    elif parser.command == 'test':
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        errors = 0
        for bp in board_providers:
            # Check
            if bp is None:
                continue
            logging.info('================')
            logging.info('Site: %s' % bp.get_description())
            links = bp.get_test_links()
            if len(links) == 0:
                logging.info('No available test link')
                continue
            if not bp.is_enabled():
                logging.info('Disabled module')
                continue

            # Pick one link only to not overload the remote server
            url, expected = choice(links)
            logging.info('Target link: %s' % url)
            logging.info('Expecting data: %s' % expected)

            # Download link
            bp.reset()
            if not bp.assign_game(url):
                data = None
            else:
                try:
                    data = bp.download_game()
                    data = bp.sanitize(data)
                except Exception:
                    logging.debug(str(Exception))
                    data = None

            # Result
            ok = data is not None
            logging.info('Fetched data: %s' % ok)
            if ok:
                logging.info(data)
            if ok != expected:
                logging.error('Test in error')
                errors += 1

        if errors > 0:
            logging.error('The unit test failed %d times' % errors)

    else:
        cmdline.print_help()


asyncio.run(main())
