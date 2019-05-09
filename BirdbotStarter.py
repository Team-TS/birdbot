from subprocess import Popen
import time
import os
import sys

def startup():
    location = os.path.join(sys.path[0],'birdbot.py')
    print(location)
    running = None
    while True:
        if running == None:
            running = Popen(['python', location])
        time.sleep(5)
startup()
