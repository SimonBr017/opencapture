#!/usr/bin/python3
import subprocess
import os


def start():
    script = './default_input.sh'
    
    dir = 'instance/upload/verifier'
    proc = subprocess.Popen(["./service_workerOC.sh"])
    
    proc

    list = os.listdir(dir)

    for i in range(len(list)):
        file = 'instance/upload/verifier/' + list[i]
        subproc = subprocess.run([script, file])
        subproc


if __name__ == '__main__':
    subprocess.run(['killall', 'kuyruk'])
    start()