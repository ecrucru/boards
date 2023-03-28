# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

# Constants
ANNOTATOR = 'ecrucru/boards@github 1.0'
BOARD_CHESS, BOARD_DRAUGHTS, BOARD_GO, BOARD_MILL = range(4)
BOARDS_DESC = ['Chess', 'Draughts', 'Go', 'Mill']
METHOD_DL, METHOD_HTML, METHOD_API, METHOD_MISC, METHOD_WS = range(5)
METHODS_DESC = ['Download link', 'HTML parsing', 'Application programming interface', 'Various techniques', 'Websockets']
TYPE_GAME, TYPE_STUDY, TYPE_PUZZLE, TYPE_SWISS, TYPE_TOURNAMENT, TYPE_EVENT, TYPE_FEN = range(7)

# Constants
CHESS960 = 'Fischerandom'
CHESS960_CLASSICAL = 518
FEN_START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_START_960 = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w HAha - 0 1'
