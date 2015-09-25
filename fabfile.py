# encoding=utf8

##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gerbrandy S.R.L.
#
# This file is part of bioport.
#
# bioport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
##########################################################################
"""
This script defines some utility functions for deployment, managing the server, etc.

It needs "fabric" to run. ("sudo apt-get install fabric" on debian).

The following command gives is a list of available commands.

>> fab -l

The script also expects to find a file secret.py in the current directory that contains information
about various installations of the software. These should have the following form:

CONFIG = {
    'production':         # the name of the deployment configuration
        'host': 'usename@hostname',   # hostname of the machine where the instance is deployed, e.g. localhost or www.bioport.example.com
        'dsn': 'mysql://username:password@hostname/databasename', # access to the mysql instance
        'db_host': 'hostname',  # where the mysql db is found
        'db_name': 'databasename',
        'db_user': 'username',
        'db_password': 'password',
    },

}

"""

import os
import copy

from fabric.contrib import console
from fabric.contrib import project
from fabric.contrib import files
from fabric.api import local, env, cd, run, put, sudo, warn, puts, get, settings, task


env.use_ssh_config = True

from secret import CONFIG

TMP_FILE = '/tmp/bioport_dump.sql'


def get_config(where):
    if where not in CONFIG:
        msg = 'Possible options are:\n'
        for k in CONFIG:
            msg += '\t{0}'.format(k)
            desc = CONFIG[k].get('description', '')
            if desc:
                msg += '\t\t- ' + desc
            msg += '\n'
        raise Exception(msg)
    config = copy.deepcopy(CONFIG['default'])
    if where == 'staging_local':
        config.update(CONFIG['staging'])
    config.update(CONFIG[where])
    config['host_string'] = config['host']
    return config


@task
def deploy(host=None):
    """update the code, and restart the all Service]
    """

    print 'deploying to %s' % host
    config = get_config(host)
    installation_directory = config['installation_directory']

    with settings(host_string=config['host']):
        with cd(installation_directory):

            run('git pull')
            run('cd src/bioport; git pull;')
            run('cd src/bioport_repository; git pull;')
            run('cd src/names; git pull;')
            run('cd src/biodes; git pull;')
            run('bin/supervisorctl shutdown')
            run('bin/buildout -vvvv -c %(config_file)s' % config)
            with settings(warn_only=True):
                run('bin/supervisord')


@task
def download_data_from_production():
    """download mysql data from production, and read it in local db"""
    copy_data('production', 'local')


@task
def copy_data(source, destination):
    if destination == 'production':
        raise Exception('Sorry, we dont copy TO production')
    src_config = get_config(source)
    dst_config = get_config(destination)
    dst_config['tmp_file'] = src_config['tmp_file'] = tmp_file = TMP_FILE

    with settings(host_string=src_config['db_host']):
        print 'dumping data'
        cmd = 'mysqldump %(db_name)s -u %(db_user)s -p%(db_password)s > %(tmp_file)s' % src_config
        print cmd
        run(cmd)

        run('tar czf %(tmp_file)s.tar.gz %(tmp_file)s' % src_config)

    # we have a dumpfile, we transfer it to the destination
    if destination == 'local':
        get(tmp_file + '.tar.gz', tmp_file + '.tar.gz')
        local('tar xzf %(tmp_file)s.tar.gz /tmp%(tmp_file)s' % dst_config)
        local('mysql bioport < %(tmp_file)s' % dst_config)

        # clean up
        local('rm /tmp%(tmp_file)s' % dst_config)
        local('rm %(tmp_file)s.tar.gz' % dst_config)
    else:
        with settings(host_string=src_config['db_host']):
            run('scp src_config[tmp_file] dst_config[db_host]:dst_config[tmp_file]'.format(**locals))
        with settings(host_string=dst_config['db_host']):

            run('tar xzf %(tmp_file)s.tar.gz /tmp%(tmp_file)s' % dst_config)
            run('mysql bioport < %(tmp_file)s' % dst_config)

            # clean up
            run('rm /tmp%(tmp_file)s' % dst_config)
            run('rm %(tmp_file)s.tar.gz' % dst_config)

    with settings(host_string=src_config['db_host']):
        run('rm %(tmp_file)s' % src_config)
        run('rm %(tmp_file)s.tar.gz' % src_config)

    return


@task
def restart(host=None):
    """restart the server on host"""
    config = get_config(host)
    installation_directory = config['installation_directory']

    with settings(host_string=config['host']):
        with cd(installation_directory):
            try:
                run('bin/supervisord')
            except:
                print 'supervisord command failed: probably because it is already running'
                print 'in that case, you can safely ignore this warning'
                pass
            run('bin/supervisorctl restart all')


@task
def commit(message=None):
    """commit all local changes"""
    if not message:
        message = console.prompt('commit message?')
    print 'committing local copy'
    local('svn ci . -m "%(message)s"' % locals())
    local('svn ci src/bioport -m "%(message)s"' % locals())
    local('svn ci src/bioport_repository -m "%(message)s"' % locals())
    local('svn ci src/biodes -m "%(message)s"' % locals())
    local('svn ci src/names -m "%(message)s"' % locals())


def tunnel_to_plone():
    local('ssh dev -L 8094:bioport:8094')


@task
def test(test=''):
    """run tests locally. The optional argument is a regexp to match names of test methods, e.g. fab test:test_something"""
    config = get_config('local')
    if test:
        local('cd {installation_directory} && bin/test -t {test}'.format(test=test, **config))
    else:
        local('cd {installation_directory} && bin/test'.format(**config))


def _run_repository_command(cmd, where):
    config = get_config(where)
    config['cmd'] = cmd
    cmd = """from bioport_repository.repository import Repository;
import logging;
logging.getLogger().setLevel(logging.INFO);
dsn = '%(dsn)s'
images_cache_local = '%(images_cache_local)s'


repository = Repository(dsn=dsn, images_cache_local=images_cache_local)
%(cmd)s""" % config

    with settings(host_string=config['host']), cd(config['installation_directory']):
        run('./bin/python-console -c "%(cmd)s"' % locals())


@task
def download_illustrations(source, host='staging'):
    """OBSOLETE (see sources/fabfile.py)
    download illustrations for the source
       arguments:
        source: a valid source_id (cf. http://test.bioport.huygens.knaw.nl/admin/sources
        host: one of 'local', 'staging', 'production'. Default is staging.

    """
    raise Exception('Sorry, obsolte, use the fabfile from bioport sources')
    cmd = """
source = repository.get_source('%(source)s')
print source
repository.download_illustrations(source=source)
""" % locals()
    _run_repository_command(cmd, host)


@task
def download_biographies(source, host='staging'):
    """OBSOLETE (see sources/fabfile.py)
    download biographies for the source
       arguments:
        source: a valid source_id (cf. test.inghist.nl/bioport/admin/sources
        host: one of 'local', 'staging', 'production'. Default is staging.

    """
    cmd = """source = repository.get_source('%(source)s')
print source
repository.download_biographies(source=source)""" % locals()
    _run_repository_command(cmd, host)


def refresh_persons_cache(host='staging'):
    """refresh the persons cache (the info of persons cached in the db table)"""

    cmd = """
persons = repository.get_persons()
logging.info('ok, lets start')
for i, person in enumerate(persons):
    logging.info(str(i) + '/' + str(len(persons)))
    person.save()

""" % locals()
    _run_repository_command(cmd, host)


@task
def export_data(where):
    """make a dump of the data"""
    config = get_config(where)
    with settings(host_string=config['host']), cd(config['installation_directory']):
        run('bin/python-console src/bioport_repository/bioport_repository/datamanipulation/export_all_data.py %(dsn)s' % config)


@task
def download_data_fs(where='production'):
    config = get_config(where)

    config['local_installation_directory'] = get_config('local')['installation_directory']
    # make a backup
#     local('mv {local_installation_directory}/var/filestorage/Data.fs {local_installation_directory}/tmp/Data.fs_backup'.format(**config))
    local('scp {host}:{installation_directory}/var/filestorage/Data.fs {local_installation_directory}/var/filestorage/'.format(**config))


@task
def info():
    """print some useful info for programmers"""
    print 'Start development server'
    print '> bin/paster serve etc/production.ini --reload'


@task
def git_pull(where):
    config = get_config(where)
    print config
    with settings(host_string=config['host']), cd(config['installation_directory']):
        run('git pull')
        run('cd src/bioport && git pull')
        run('cd src/bioport_repository && git pull')
