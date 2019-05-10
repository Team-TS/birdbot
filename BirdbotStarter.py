from subprocess import Popen
import time
import os
import sys

def startup():
    location = os.path.join(sys.path[0],'birdbot.py')
    print("Bot Startup Script initialised...")
    while True:
        running = Popen(['python', location])
        running.wait()
        print("The bot has just crashed... Restarting.")
startup()
