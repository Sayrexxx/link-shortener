from urllib.parse import urlparse
import re


class URLValidator:
    @staticmethod
    def is_valid(url: str) -> bool:
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            if result.scheme not in ('http', 'https'):
                return False
            netloc = result.netloc.lower()
            if netloc.startswith(('localhost', '127.', '::1', '0.0.0.0')):
                return False
            if not re.match(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', netloc.split(':')[0]):
                return False
            return True
        except:
            return False

    @staticmethod
    def normalize(url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url
