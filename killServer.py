'''
Run in a seperate RPi terminal.  Kills the server process and
all of the threads it may have started.  Slightly hackish.
'''

import subprocess

def killSrvr():
    # Get all processes.
    result = subprocess.run(['ps','aux'],
             stdout=subprocess.PIPE,text=True, check = False)
    rspStr = result.stdout.strip()
    lines = rspStr.splitlines()

    # Get all processes that are running the python server.
    pythonServerLines = []
    for line in lines:
        if 'python' and 'server' in line:
            pythonServerLines.append(line)

    # Get all pids of processes that are running the python server.
    pythonServerPids = []
    for line in pythonServerLines:
        splitLine  = line.split()
        processNum = splitLine[1]
        pythonServerPids.append(processNum)

    # Kill all pids of python servers.
    for pid in pythonServerPids:
        result = subprocess.run( [ 'kill','-9', pid ],
                                  stdout = subprocess.PIPE,
                                  text   = True,
                                  check  = False
                               )
#############################################################################

if __name__ == '__main__':
    killSrvr()
