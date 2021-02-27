# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

# Constants
ANNOTATOR = 'ecrucru/boards@github 1.0'
BOARD_CHESS, BOARD_DRAUGHTS, BOARD_GO = range(3)
TYPE_GAME, TYPE_STUDY, TYPE_PUZZLE, TYPE_EVENT, TYPE_FEN = range(5)

# Strategies
METHOD_DL = 'Download link'
METHOD_HTML = 'HTML parsing'
METHOD_API = 'Application programming interface'
METHOD_MISC = 'Various techniques'
METHOD_WS = 'Websockets'

# Constants
CHESS960 = 'Fischerandom'
FEN_START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_START_960 = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w HAha - 0 1'
