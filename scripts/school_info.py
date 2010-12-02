#!/usr/bin/env python
import os
import sys
import time
import hashlib
from Utility import EXIF

from ConfigParser import SafeConfigParser

config = SafeConfigParser()
#This needs to change based on the whole path to the images
pathtoimgs = '/home/megha/www/klpwww/'
config.read(pathtoimgs+'config/klpconfig.ini')
#config.read(os.path.join(os.getcwd(),'config/klpconfig.ini'))
src = pathtoimgs + config.get('Pictures','origpicpath')
dst = pathtoimgs + config.get('Pictures','hashpicpath')

tag = 'EXIF DateTimeOriginal'
data_file = 'data/school_info.lst'
sys_sql_file = 'sql/tb_sys_data.sql'
sch_sql_file = 'sql/tb_school_info.sql'
img_sql_file = 'sql/tb_sys_images.sql'

def addslashes(arr):
  newarr = []
  d = {'"':'""', "'":"''", "\\":"\\\\" }
  for s in arr:
    newarr.append(''.join(d.get(c, c) for c in s))
  return newarr 

def getDate(origdate):
  splits=origdate.split(" ")
  dates=splits[0].split(":")
  return dates[2]+"-"+dates[1]+"-"+dates[0]

def processImage(image,schoolid):
  tags=EXIF.process_file(image)
  retdate=getDate(str(tags[tag]))
  return retdate 

def processSYS(images,schoolid,id_counter):
  try:
    retdates = []
    for image in images:
      if(len(image) > 0):
        image = image.rstrip('\n') + ".jpg"
        if os.path.exists(src + image):
          retdate = processImage(open(src + image, 'rb'),schoolid)
          if retdate not in retdates: # id should be updated only if the images return different dates making it two SYS for two diff visits
            retdates.append(retdate)
            id_counter = id_counter + 1
            sys_sql = "INSERT INTO tb_sys_data(id,schoolid,name,dateofvisit) values("+str(id_counter) + "," + str(schoolid)+",'LOCALCIRCLE','"+retdate+"');" 
            sysf.write(sys_sql + "\n")
          hash_name = hashlib.md5(open(src + image,'r').read()).hexdigest() + '.jpg'
          #Comment out the following two lines if the Image magick resizing is done
          #os.system('convert ' + src + image + ' -resize 25% ' + dst + hash_name )
          #print 'convert ' + src + image + ' -resize 25% ' + dst + hash_name
          #-------
          img_sql= "INSERT INTO tb_sys_images(schoolid,original_file,hash_file,sysid,verified) values("+str(schoolid)+",'"+image+"','"+hash_name+"',"+ \
                   str(id_counter) + ",'Y');" # Images coming in from this flow are already verified.
          imgf.write(img_sql + "\n")
  except:
    print "Sorry:", sys.exc_type, ":", sys.exc_value, "while processing image:", image
  return id_counter


#-----MAIN-------
try:
  sysf = open(sys_sql_file, 'a')
  schf = open(sch_sql_file, 'a')
  imgf = open(img_sql_file, 'a')
  rf = open(data_file, 'r')
  id_counter = 300
  for line in rf.readlines():
    data = line.split('|')
    try:
      schoolid = int(data[0])
      si_sql = "INSERT into tb_school_info values (" + data[0] + ",'"+ addslashes([data[1]])[0] + "','" + "','".join(addslashes(data[2:9])) + "');"
      schf.write(si_sql + "\n")
      datalen = len(data)
      id_counter = processSYS(data[9:datalen],data[0],id_counter)
      print "ID counter:" + str(id_counter)
    except:
      print "School ID:" + data[0] + " could not be processed"
except:
  print "Sorry:", sys.exc_type, ":", sys.exc_value, "while on line:", line
finally:
  schf.close()
  sysf.close()
  rf.close()
