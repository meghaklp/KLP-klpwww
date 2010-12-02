#!/usr/bin/env python
import os
import sys
from datetime import date

data_file = 'data/sys_data.lst'
sys_sql_file = 'sql/tb_sys_data_prod.sql'

def addslashes(arr):
  newarr = []
  d = {'"':'""', "'":"''", "\\":"\\\\" }
  for s in arr:
    newarr.append(''.join(d.get(c, c) for c in s))
  return newarr

def formatDate(str):
  if '/' in str:
    datearr = str.split('/')
    if len(datearr[2])<4:
      datearr[2] = "20" + datearr[2]
    d = date(int(datearr[2].strip()),int(datearr[1].strip()) , int(datearr[0].strip()) )
    str = d.strftime("%d-%m-%Y")
  return str


#-----MAIN-------
try:
  sysf = open(sys_sql_file, 'w')
  rf = open(data_file, 'r')
  for line in rf.readlines():
    data = line.split('|')
    try:
      si_sql = "INSERT into tb_sys_data "+ \
                "(id,schoolid,name,email,telephone,dateofvisit,comments,entered_timestamp) values (" + \
                data[0].strip() + ","+ data[1].strip() + ",'" + data[2] + "','" + data[3] + "','" + data[4] + "','" + formatDate(data[5]) + "','" + \
                addslashes([data[6]])[0] + "','" + data[7].rstrip('\n') + "');"
      sysf.write(si_sql + "\n")
    except:
      print "Sorry:", sys.exc_type, ":", sys.exc_value, "while on line:", data[0] 
except:
  print "Sorry:", sys.exc_type, ":", sys.exc_value, "while on line:", line
finally:
  sysf.close()
  rf.close()
