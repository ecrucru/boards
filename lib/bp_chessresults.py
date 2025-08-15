# Copyright (C) 2025 ecrucru
# https://github.com/ecrucru/boards
# GPL version 3

from typing import Optional, List, Tuple
from urllib.parse import urlparse
import re

from lib.const import BOARD_CHESS, METHOD_HTML
from lib.bp_interface import InternetGameInterface


# Chess-Results.com
class InternetGameChessresults(InternetGameInterface):
    def get_identity(self) -> Tuple[str, int, int]:
        return 'Chess-Results.com', BOARD_CHESS, METHOD_HTML

    def assign_game(self, url: str) -> bool:
        # Verify the host
        parsed = urlparse(url)
        if not ('.' + parsed.netloc.lower()).endswith('.chess-results.com'):
            return False

        # Read the identifier
        m = re.compile(r'tn(o|r)=?(\d+)').search(url)
        if m is not None:
            self.id = m.group(2)
            return True
        return False

    def download_game(self) -> Optional[str]:
        # Payload
        payload = {'ctl00$P1$combo_anzahl_zeilen': '5',         # 2000
                   'ctl00$P1$cb_SuchenPartie': 'Search',
                   'ctl00$P1$txt_von_tag': '',
                   'ctl00$P1$txt_bis_tag': '',
                   'ctl00$P1$txt_rdbis': '16',
                   'ctl00$P1$txt_rdvon': '1',
                   'ctl00$P1$txt_dbkey': self.id,
                   'ctl00$P1$txt_bez': '',
                   'ctl00$P1$txt_vorname': '',
                   'ctl00$P1$Txt_FideID': '',
                   'ctl00$P1$Txt_NatID': '',
                   'ctl00$P1$txt_nachname': '',
                   'ctl00$P1$combo_spielerfarbe': '-',
                   'ctl00$P1$combo_ergebnis': '-'}

        # Perform a search in 2 attempts to load the cache
        url = 'https://s3.chess-results.com/partieSuche.aspx?lan=1&tnr=%s&art=4&rd=1' % self.id
        for i in range(2):
            data = self.send_xhr(url, payload)
            assert (data is not None) and ('Internal Server Error' not in data)

            # Update the event data
            for t in ['__EVENTARGUMENT', '__EVENTTARGET', '__EVENTVALIDATION', '__VIEWSTATE', '__VIEWSTATEGENERATOR']:
                m = re.compile('id="%s" value="(.*)"' % t).search(data)
                if m is not None:
                    payload[t] = m.group(1)
                else:
                    payload[t] = ''

        # Download the games
        del payload['ctl00$P1$cb_SuchenPartie']
        payload['ctl00$P1$cb_DownLoadPGN'] = 'Download as PGN-File'
        return self.send_xhr(url, payload)

    def get_test_links(self) -> List[Tuple[str, bool]]:
        return [('https://chess-results.com/tnr424416.aspx', True),                                 # Old games
                ('https://chess-results.com/tnr1129984.aspx?lan=1', True),                          # Recent games
                ('https://chess-results.com/tnr1080336.aspx', False),                               # No game
                ('https://s3.chess-results.com/tnrWZ.aspx?tno=1113047', True),                      # Recent games
                ('https://archive.chess-results.com/PartieSuche.aspx?art=36&id=1003812', False),    # TODO Single game not supported
                ]
