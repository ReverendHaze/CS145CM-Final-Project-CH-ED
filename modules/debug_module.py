import time
import random
from modules.config_module import load_settings

class Logger:
    logfile_name = ''

    def __init__(self):
        config = load_settings()
        topics = config['NUM_TOPICS']
        beta = config['BETA']
        self.logfile_name = 'out/logs/{}_{}.log'.format(topics, beta)

    def tprint(self, print_string):
        print('{}: {}'.format(time.strftime("%H:%M:%S"), print_string))
        f = open(self.logfile_name, 'a+')
        f.write(str(print_string))
        f.write('\n')
        f.close()

