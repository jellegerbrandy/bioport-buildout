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

CONFIG = {
    'production': {         # the name of the deployment configuration
        'host': 'usename@hostname',   # hostname of the machine where the instance is deployed, e.g. localhost or www.bioport.example.com
        'dsn': 'mysql://username:password@hostname/databasename', # access to the mysql instance
        'db_host': 'hostname',  # where the mysql db is found
        'db_name': 'databasename',
        'db_user': 'username',
        'db_password': 'password',
    },

}


try:
    from mysecret import CONFIG
except:
    pass
