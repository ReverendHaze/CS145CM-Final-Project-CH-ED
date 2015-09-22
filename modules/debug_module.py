import time
import random
import os
from modules.config_module import load_settings

class Logger:
    logfile_name = ''
    enabled = False

    def __init__(self):
        config = load_settings()
        topics = config['NUM_TOPICS']
        beta = config['BETA']
        self.logfile_name = 'out/logs/{}_{}.log'.format(topics, beta)
        if not self.enabled:
            try:
                os.remove(self.logfile_name)
            except:
                pass
            self.enabled = True

    def tprint(self, print_string):
        print_string = '{}: {}'.format(time.strftime("%H:%M:%S"), print_string)
        f = open(self.logfile_name, 'a+')
        f.write(print_string)
        f.write('\n')
        f.close()

