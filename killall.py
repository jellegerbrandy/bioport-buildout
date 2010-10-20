# kills all instances

import psutil
import os

CWD = os.getcwd()

for p in psutil.process_iter():
    cmdline = ' '.join(p.cmdline)
    if 'python' in cmdline and CWD in cmdline:
        p.kill()

