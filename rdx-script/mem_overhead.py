import sys
import os
#import getopt
#import copy
#import random
import shlex, subprocess
import time
import fcntl
#import fnmatch
#import ntpath
#import shutil
#import csv
import threading
from fcntl import flock, LOCK_EX, LOCK_SH, LOCK_UN


#--------------------------------------
# run command, get memory usage
#--------------------------------------
accu_size = 0
count = 0
class MemMonitor(threading.Thread):
    def __init__(self,peak, pid):
        threading.Thread.__init__(self)
        self.peak = 0L
        self.pid = pid
    def run(self):
       global accu_size
       global count
       while True:
           cmd = ['ps', '-p', str(self.pid), '-o' , 'rss=']
           process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
           (sout, serr) = process.communicate()
           if process.returncode != 0:
               break
           if self.peak < long(sout): self.peak = long(sout)
           count += 1
           accu_size += long(sout)
           time.sleep(.001)
       print(accu_size/count)

def MemRun(command, input, output=True):
    #t1 = time.time()
    process = subprocess.Popen(shlex.split(command),bufsize=-1,shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # launch a side thread to monitor the peak memory
    thread1 = MemMonitor(0, process.pid)
    thread1.start()

    (sout, serr) = process.communicate(input)
    #t2 = time.time()

    thread1.join()
    #assert(process.returncode == 0)
    if output:
        sys.stdout.write(sout)
        sys.stderr.write(serr)
    #t = t2 - t1
    return  thread1.peak


ipSz =  os.fstat(sys.stdin.fileno()).st_size
sin = None
if ipSz > 0 :
    sin = sys.stdin.read()

cmd = ''
argIter = iter(sys.argv[1:])
for arg in argIter:
    cmd = cmd + ' ' + arg

orgRSS = MemRun(cmd,sin,True)

#f = open('/home/psu/peak_memory.txt','a')
f = open('/home/bli11/jxperf/peak_memory.run','a')
fcntl.flock(f.fileno(), LOCK_EX)
# f.write(cmd + ', peak memory: ' + str(orgRSS) + "KB" + ' average memory: ' + str(accu_size/count) + "KB" + '\n')
f.write(str(accu_size/count) + '\n')
fcntl.flock(f.fileno(), LOCK_UN)
f.close()
