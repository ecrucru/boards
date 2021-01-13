# Copyright (C) 2019-2020 Pychess
# Copyright (C) 2021 ecrucru
# https://github.com/ecrucru/chess-dl
# GPL version 3

import re

# Constants
ANNOTATOR = 'chess-dl 0.1'
TYPE_GAME, TYPE_STUDY, TYPE_PUZZLE, TYPE_EVENT, TYPE_FEN = range(5)
CHESS960 = 'Fischerandom'
FEN_START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
FEN_START_960 = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w HAha - 0 1'

# Precompiled regular expressions
REGEX_STRIP_HTML = re.compile(r'<\/?[^>]+>', re.IGNORECASE)
REGEX_FEN = re.compile(r'^[kqbnrp1-8\/]+\s[w|b]\s[kq-]+\s[a-h-][1-8]?(\s[0-9]+)?(\s[0-9]+)?$', re.IGNORECASE)

# Strategies
CAT_DL = 'Download link'
CAT_HTML = 'HTML parsing'
CAT_API = 'Application programming interface'
CAT_MISC = 'Various techniques'
CAT_WS = 'Websockets'
