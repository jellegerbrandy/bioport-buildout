#!/usr/bin/env python2.5

"""Sources manager script"""

import optparse
import sys
import os
import logging

import biodes
from bioport_repository.repository import Repository
from bioport_repository.illustration import CantDownloadImage
from bioport_repository.biography import Biography
from bioport_repository.source import Source


DEFAULT_IMAGES_DIR = "/var/bioport/images_test"
DEFAULT_DB = "mysql://root@localhost/bioport"
#TOTAL_BIOS = _repo.count_biographies()
#TOTAL_PERSONS = _repo.count_persons()
#IMAGES_DIR = _repo.images_cache_local  


# --- private API

def setup_logger(level=logging.WARNING):
    """Redirects the standard logger used in bioport and 
    bioport_repository packages to stderr.
    
    By default it shows only messages with a priority level >= WARNING.
    Call it with logging.DEBUG as an argument for complete verbosity.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)

setup_logger()


def get_ids():
    """Return the IDs of all defined sources"""
    return [src.id for src in _repo.get_sources()]


# --- public API 

def list_sources():
    print "\ntotal biographies: %s"  %_repo.count_biographies()
    print "\ntotal persons: %s\n" %_repo.count_persons()
    print "ID        QUANTITY   QUALITY  DESCRIPTION"
    print "=========================================\n"
    for src in _repo.get_sources(order_by="id", desc=True):
        quantity = _repo.count_biographies(source=src)        
        line = "%-9s %-10s %-8s %-5s\n" % (src.id, quantity, src.quality, 
                                           src.description)
        line = line.replace("\r\n", "")
        print line


def download_illustrations(id, overwrite):
    if id not in get_ids():
        raise ValueError("No source with id '%s' was found" % id)
    for src in _repo.get_sources():
        if src.id == id:
            break
    bios = _repo.get_biographies(source=src)
    total = len(bios)
    skipped = 0
    for index, bio in enumerate(bios):   
        print "%s/%s " % (index + 1, total)
        for ill in bio.get_illustrations():
            try:
                ill.download(overwrite=overwrite)
            except CantDownloadImage, err:
                skipped += 1
                print err
    print "total:%(total)s skipped:%(skipped)s" % locals()
    
    
def download_biographies(id):
    if id not in get_ids():
        raise ValueError("No source with id '%s' was found" % id)
    for src in _repo.get_sources():
        if src.id == id:
            break

    ls = biodes.parse_list(src.url)
    total = len(ls)
    skipped = 0
    for index, biourl in enumerate(ls):
        print "%s/%s " % (index + 1, total)
        if not biourl.startswith("http:"):
            # we're dealing with a fs path
            biourl = os.path.normpath(biourl)
            if not os.path.isabs(biourl):
                biourl = os.path.join(os.path.dirname(src.url), biourl)

        bio = Biography(source_id=src.id, repository=src.repository)
        try:
            bio.from_url(biourl)
        except Exception, err:
            skipped += 1
            print err
            continue

        _repo.add_biography(bio)

    print "total:%(total)s skipped:%(skipped)s" % locals()
    _repo.delete_orphaned_persons(source_id=src.id)


def delete_source(id):
    """Delete source with given id"""
    _repo.delete_source(Source(id, '', ''))
    print "deleted source with id " + id

def delete_biographies(id):
    """Delete source with given id"""
    _repo.delete_biographies(Source(id, '', ''))
    print "deleted biographies of source with id " + id

def add_source(id, url, descr):
    """Add source with given id, url and description"""
    src = Source(id, url, descr)
    _repo.add_source(src)
    print "added source with id " + id

def refresh_similarity_table(id):
    """Refresh similarity table of source with given id."""
    if not id in get_ids():
        # XXX - this should be checked in db.fill_similarity_cache but 
        # it isn't; I'd say it's an application bug
        raise ValueError("no source with id %s was found" % id)
    _repo.db.fill_similarity_cache(refresh=True, source_id=id)
    print "similarity table of source with id %s refreshed" % id

    
def main():
    global _repo
    class CustomizedOptionFormatter(optparse.IndentedHelpFormatter):
        """Formats options shown in help in a prettier way."""

        def format_option(self, option):
            result = []
            opts = self.option_strings[option]
            result.append('  %s\n' % opts)
            if option.help:
                help_text = '     %s\n\n' %self.expand_default(option)
                result.append(help_text)
            return ''.join(result)
    
    parser = optparse.OptionParser()
    parser.add_option('-l', '--list', action='store_true',
                      help="list all available sources")
    parser.add_option('-a', '--add-source', metavar="ID,URL,DESCRIPTION",
                      help="add new source with given id, url and descrption "
                           "(comma separated values)")
    parser.add_option('-i', '--illustrations', metavar="ID",
                      help="download illustrations of source ID")
    parser.add_option('-b', '--biographies', metavar="ID",
                      help="download biogrpahies of source ID")
    parser.add_option('-o', '--overwrite', default=False, action='store_true',
                      help="if specified re-download and overwrite existing "\
                            "files when downloading illustrations" )
    parser.add_option('--ds', '--delete-source', metavar="ID",
                      help="delete source given it ID")
    parser.add_option('--db', '--delete-biographies', metavar="ID",
                      help="delete source given it ID")
    parser.add_option('-r', '--refresh-similarity-table', metavar="ID",
                      help="refresh similarity table of source with given ID")
    parser.add_option('-s', '--sqldb', default=DEFAULT_DB, metavar="DBURL",
                      help='sql database connection url (defaults to %s)' % DEFAULT_DB)
    parser.add_option('-d', '--directory', default=DEFAULT_IMAGES_DIR, metavar="DIRECTORY",
                      help='the directory where the illustrations will be stored ' \
                           '(defaults to %s)' % DEFAULT_IMAGES_DIR)
    parser.add_option('-v', '--verbose', default=False, action='store_true',
                      help="verbose mode")

    options, args = parser.parse_args()
    _repo = Repository(db_connection=options.sqldb, 
                       images_cache_local=options.directory) 
    if options.verbose:
        setup_logger(logging.DEBUG)
    if options.list:
        list_sources()
        sys.exit(0)
    if options.illustrations:
        download_illustrations(options.illustrations, options.overwrite)
        sys.exit(0)
    if options.biographies:
        download_biographies(options.biographies)
        sys.exit(0)
    if options.ds:
        delete_source(options.ds)
        sys.exit(0)
    if options.db:
        delete_biographies(options.db)
        sys.exit(0)
    if options.add_source:
        if options.add_source.count(',') != 2:
            parser.error('needs comma separated values such as "id,url,descr"')
        id, url, descr = options.add_source.split(',')
        add_source(id, url, descr)
        sys.exit(0)
    if options.refresh_similarity_table:
        refresh_similarity_table(options.refresh_similarity_table)
        sys.exit(0)


if __name__ == '__main__':
    main()

