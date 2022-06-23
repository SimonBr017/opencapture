#!/usr/bin/python3

import subprocess
import sys

def start_per_file(args):

    script = 'bin/script/default_input_per_file.sh'

    file_path = args[1]

    subproc = subprocess.Popen([script, file_path])

    subproc


if __name__ == '__main__':

    start_per_file(sys.argv)
