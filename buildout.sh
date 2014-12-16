cfg=$1 || $bram.cfg
python bootstrap.py -v 1.7.0 -c $cfg && \
bin/buildout -vv -c $cfg

