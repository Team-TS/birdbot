from subprocess import Popen
import subprocess
import time
import os
import sys

def startup():
    location = os.path.join(sys.path[0],'birdbot.py')
    locationBAT = os.path.join(sys.path[0],'YTDLUpdate.bat')
    print("Bot Startup Script initialised...")
    while True:
        subprocess.call([locationBAT])
        running = Popen(['python', location])
        running.wait()
        print("The bot has just crashed... Restarting.")
startup()
