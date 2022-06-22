#!/usr/bin/python3

import subprocess
import sys
import time

def start_per_file(args):
    
    script = 'bin/script/default_input_per_file.sh'
    
    file_path = args[1]

    service_worker = subprocess.Popen(["bin/script/service_workerOC.sh"])
    
    service_worker

    time.sleep(2)

    subproc = subprocess.run([script, file_path])

    subproc
    

if __name__ == '__main__':

    start_per_file(sys.argv)
