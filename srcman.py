import optparse

from bioport_repository.repository import Repository


IMAGES_DIR = "/var/bioport/images_test"
SQL_DB = "mysql://root@localhost/bioport"

HELP_PROGRAM = """help program"""


def list_sources(repo):
    print
    print "ID        QUALITY    DESCRIPTION"
    print "================================="
    print
    for src in repo.get_sources(order_by="id", desc=True):
        line = "%-9s %-10s %-5s\n" % (src.id, src.quality, src.description)
        line = line.replace("\r\n", "")
        print line

if __name__ == '__main__':
    repo = Repository(db_connection=SQL_DB, images_cache_local=IMAGES_DIR)
    usage = "python -m pyftpdlib.ftpserver [options]"
    parser = optparse.OptionParser(usage=usage, description=HELP_PROGRAM)
    parser.add_option('-l', '--list', action='store_true',
                      help="list all available sources")

    options, args = parser.parse_args()
    if options.list:
        list_sources(repo)
    
