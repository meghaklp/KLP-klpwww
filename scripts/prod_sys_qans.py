#!/usr/bin/env python
import os
import sys
import time

data_file = 'data/sysimages/sys_qans'
sys_sql_file = 'sql/tb_sys_qans_prod.sql'


#-----MAIN-------
try:
  sysf = open(sys_sql_file, 'w')
  rf = open(data_file, 'r')
  for line in rf.readlines():
    data = line.split('|')
    try:
      si_sql = "INSERT into tb_sys_qans (sysid, qid, answer) values (" + data[0].strip() + ","+ data[1].strip() + ",'" + data[2].strip().rstrip('\n') + "');"
      sysf.write(si_sql + "\n")
    except:
      print "SYS ID:" + data[0] + " could not be processed"
except:
  print "Sorry:", sys.exc_type, ":", sys.exc_value, "while on line:", line
finally:
  sysf.close()
  rf.close()
