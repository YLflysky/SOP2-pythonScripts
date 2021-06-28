from box.base import Base
import random
from box.lk_logger import lk
import os

class Cert(Base):
    '''
    商城API
    '''
    def __init__(self):
        super().__init__()
        self.url = None