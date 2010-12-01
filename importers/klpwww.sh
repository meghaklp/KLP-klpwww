#!/bin/sh

DBNAME=$(basename $0 .sh)
OWNER=klp

#sudo -u postgres dropuser ${OWNER}
#sudo -u postgres createuser -S -D -R -E -P ${OWNER}

sudo -u postgres dropdb ${DBNAME}
sudo -u postgres createdb -O ${OWNER} -E UTF8 ${DBNAME}
# Setup dblink
sudo -u postgres psql -d ${DBNAME} -f /usr/share/postgresql/8.4/contrib/dblink.sql

# For the types that will be queried through the dblink to klp_coord
sudo -u postgres createlang plpgsql ${DBNAME}
sudo -u postgres psql -d ${DBNAME} -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
sudo -u postgres psql -d ${DBNAME} -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql
# Grant privileges
sudo -u postgres psql -d ${DBNAME} -f grants.sql

# Create schema
psql -U ${OWNER} -d ${DBNAME} -f ${DBNAME}.sql 

# Load ${DBNAME}
perl klp-exp.pl
echo Loading data into ${DBNAME}
sudo -u postgres psql -d ${DBNAME} -f load/load.sql
echo Computing aggregates for ${DBNAME}
psql -U ${OWNER} -d ${DBNAME} -f agg.sql 

# Data inserts for SYS, Pics and School Page
sudo -u postgres psql -d ${DBNAME} -f load/tb_school_info.sql
sudo -u postgres psql -d ${DBNAME} -f load/tb_sys_data.sql
sudo -u postgres psql -d ${DBNAME} -f load/tb_sys_images.sql
sudo -u postgres psql -d ${DBNAME} -f load/tb_sys_qans.sql

# Perform data workarounds
psql -U ${OWNER} -d ${DBNAME} -f fixes.sql 
