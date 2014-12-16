cfg=$1 || $bram.cfg
python bootstrap.py -v 1.5.1 -c $cfg && \
bin/buildout -c $cfg
# more verbose:
#bin/buildout -vv -c $cfg
(cd plone-buildout && python bootstrap.py && bin/buildout)
