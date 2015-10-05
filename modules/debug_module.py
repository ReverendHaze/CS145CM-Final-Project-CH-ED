import time
import random
import os
from modules.config_module import load_settings
from modules.utils import rm

class Logger:
    logfile_name = ''
    enabled = False

    def __init__(self):
        config = load_settings()
        config_hash = hash(frozenset(config))
        self.logfile_name = 'out/logs/{}.log'.format(config_hash)
        if not self.enabled:
            rm(self.logfile_name)
            rm('current.log')
            os.symlink(self.logfile_name, 'current.log')
            self.enabled = True

    def tprint(self, print_string):
        print_string = '{}: {}'.format(time.strftime("%H:%M:%S"), print_string)
        f = open(self.logfile_name, 'a+')
        f.write(print_string)
        f.write('\n')
        f.close()

