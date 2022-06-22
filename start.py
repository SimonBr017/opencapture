#!/usr/bin/python3
import subprocess
import os
import json

def start():
    script = 'bin/script/default_input.sh'
    
    dir = 'instance/upload/verifier'
    service_worker = subprocess.Popen(["bin/script/service_workerOC.sh"])
    
    service_worker

    list = os.listdir(dir)

    for i in range(len(list)):
        file = 'instance/upload/verifier/' + list[i]
        subproc = subprocess.run([script, file])
        subproc


if __name__ == '__main__':

    subprocess.run(['killall', 'kuyruk'])
    start()
