from random import choice, randint
from pychess import VERSION

last_user_agent = None


def generate_user_agent(fake, renew=False):
    global last_user_agent
    if not fake:
        return 'PyChess %s' % VERSION
    else:
        # Reuse the last known user agent
        if not renew and last_user_agent is not None:
            return last_user_agent

        # New fake user agent
        engine = ['Mozilla/3.0', 'Mozilla/4.0', 'Mozilla/5.0', 'Opera/4.0', 'Opera/5.0']
        os = ['compatible', 'Linux', 'Ubuntu', 'SunOS', 'Macintosh', 'Windows', 'Windows 98', 'Windows NT 5.0', 'Windows NT 5.1', 'Windows NT 5.2', 'Windows NT 6.0', 'Windows NT 6.1', 'Windows NT 6.2', 'Windows NT 6.3', 'Windows NT 10.0', 'X11']
        arch = ['U', 'Linux i686', 'Intel Max OS X']
        lang = ['aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az', 'ba', 'be', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'br', 'bs', 'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy', 'da', 'de', 'dv', 'dz', 'ee', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'gv', 'ha', 'he', 'hi', 'ho', 'hr', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'ka', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ku', 'kv', 'kw', 'ky', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'my', 'na', 'nb', 'nd', 'ne', 'ng', 'nl', 'nn', 'no', 'nr', 'nv', 'ny', 'oc', 'oj', 'om', 'or', 'os', 'pa', 'pi', 'pl', 'ps', 'pt', 'qu', 'rc', 'rm', 'rn', 'ro', 'ru', 'rw', 'sa', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu']  # ISO 639-1/2/3
        rev = 'rv:%d.%d.%d.%d' % (randint(1, 2), randint(0, 9), randint(0, 9), randint(0, 9))
        product = ['Gecko', 'Firefox', 'Chrome']
        release = randint(32, 75)
        last_user_agent = '%s (%s; %s; %s; %s) %s/%d.0' % (choice(engine), choice(os), choice(arch), choice(lang), rev, choice(product), release)
        return last_user_agent
