from enum import Enum

class Environment(Enum):
    DEV = 0
    SIT = 1
    UAT = 2

class EntryPoint():
    _ENV_URL = {
        Environment.DEV : 'http://62.234.199.217:18010',
        Environment.SIT : 'http://152.136.8.194:18010',
        Environment.UAT : 'http://62.234.196.101:18010'
    }

    @property
    def url(self):
        return self._ENV_URL[host]

host = Environment.DEV
print(EntryPoint().url)