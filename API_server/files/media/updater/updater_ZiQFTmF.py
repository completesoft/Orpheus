import time
import sys
import os
import subprocess


pid = int(sys.argv[1])
cmd = 'python api_player.py'.split()
s_pid = os.getpid()
### Put here script payload


###
time.sleep(2)
subprocess.Popen(cmd)
sys.exit(0)