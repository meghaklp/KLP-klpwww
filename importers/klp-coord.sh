#!/bin/sh

DBNAME=klp-coord
OWNER=klp

sudo -u postgres dropdb ${DBNAME}
sudo -u postgres createdb -E UTF-8 -O ${OWNER} ${DBNAME}
sudo -u postgres createlang plpgsql ${DBNAME}

sudo -u postgres psql -d ${DBNAME} -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
sudo -u postgres psql -d ${DBNAME} -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql
# Grant privilges
sudo -u postgres psql -d ${DBNAME} -f grants.sql

echo -n Creating schema...
psql -U ${OWNER} -d ${DBNAME} -f ${DBNAME}.sql && echo done.

echo Loading data...
psql -U ${OWNER} -d ${DBNAME} -f load/load-klp-coord.sql && echo done.
