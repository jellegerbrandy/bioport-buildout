# terminates all instances

import psutil
import os


def main():
    thisdir = os.getcwd()
    done = False

    for p in psutil.process_iter():
        cmdline = ' '.join(p.cmdline)
        if 'python' in cmdline and thisdir in cmdline:
            print "terminating: " + str(p)
            p.terminate()
            done = True

    if not done:
        print "no active instances were found"

if __name__ == '__main__':
    def main()