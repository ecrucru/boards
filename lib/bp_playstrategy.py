# Copyright (C) 2023 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import List, Tuple

from lib.bp_libase import InternetGameLibase


# PlayStrategy.org
class InternetGamePlaystrategy(InternetGameLibase):
    def __init__(self):
        InternetGameLibase.__init__(self)
        self.set_options_li('playstrategy.org', '', True, 'pgn', '(No puzzle)')
        del self.regexes['broadcast']
        del self.regexes['practice']
        del self.regexes['puzzle']

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://playstrategy.org/8SbfJMDB', True),                # American/English
                ('https://playstrategy.org/dwm84VIU', True),                # Antichess
                ('https://playstrategy.org/WBaWL6MC', True),                # Antidraughts
                ('https://playstrategy.org/2c0fImgC', True),                # Atomic
                ('https://playstrategy.org/nQEBdx3y', True),                # Brazilian
                ('https://playstrategy.org/1WTh88zf', True),                # Breakthrough
                ('https://playstrategy.org/GGVE0iuk', True),                # Bullet
                ('https://playstrategy.org/QuWKtmbh', True),                # Chess960
                ('https://playstrategy.org/qCnZi5VC', True),                # Crazyhouse
                ('https://playstrategy.org/EjRbn6wh', True),                # Five-check
                ('https://playstrategy.org/k0rreC1j', True),                # Frisian
                ('https://playstrategy.org/wAv1R22k', True),                # Frysk!
                ('https://playstrategy.org/Wa1PcHhD', True),                # Grand Othello
                ('https://playstrategy.org/1YQqTqdr', True),                # Horde
                ('https://playstrategy.org/xp8fu8i6', True),                # International
                ('https://playstrategy.org/6675i0bY', True),                # King of the Hill
                ('https://playstrategy.org/6LufQCSv', True),                # Lines Of Action
                ('https://playstrategy.org/hk18UQay', True),                # Mini Shogi
                ('https://playstrategy.org/CPQfhCpD', True),                # Mini Xiangqi
                ('https://playstrategy.org/WFkDgTaM', True),                # No Castling
                ('https://playstrategy.org/b6vcCdWm', True),                # Othello
                ('https://playstrategy.org/dw2OZDmI', True),                # Oware
                ('https://playstrategy.org/g2M6zfBM', True),                # Pool
                ('https://playstrategy.org/KZVLyeZ4', True),                # Racing Kings
                ('https://playstrategy.org/6fi5EwGU', True),                # Russian
                ('https://playstrategy.org/2Z1N9EiY', True),                # Scrambled Eggs
                ('https://playstrategy.org/kHgORJHL', True),                # Shogi
                ('https://playstrategy.org/ZJNT8WNv', True),                # Spanish
                ('https://playstrategy.org/EjRbn6wh', True),                # Three-check
                ('https://playstrategy.org/PDyi6zcM', True),                # Togyzkumalak
                ('https://playstrategy.org/A6wpqq54', True),                # Xiangqi
                ('https://playstrategy.org/tournament/U4fTxT6b', True),     # Tournament
                ('https://playstrategy.org/swiss/h0Y3V8o7', True),          # Swiss
                ('https://playstrategy.org/study/f3AH1wUw', True),          # Study
                ('https://playstrategy.org', False),                        # Not a game (homepage)
                ]
