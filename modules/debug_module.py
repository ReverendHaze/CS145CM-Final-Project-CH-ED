import time
import random

class Logger:


    def pad(string, length):
        return '0'*(length-len(string))+string

    logfile_name = 'out/logs/{}.log'.format(pad(str(random.randint(0,999999)), 6))
    #def init(self):

    def tprint(print_string):
        print('{}: {}'.format(time.strftime("%H:%M:%S"), print_string))
        f = open(Logger.logfile_name, 'a+')
        f.write(str(print_string))
        f.write('\n')
        f.close()


