#!/usr/bin/env python
import hashlib,os


imgdir = '/home/megha/www/klpwww/scripts/data/sysimages/'
images = os.listdir(imgdir)
sqlf = open('sql/tb_sys_images_prod.sql','w')
for img in images:
  if "jpg" in img or "JPG" in img:
    data = img.split('_')
    sql = "insert into tb_sys_images (schoolid,sysid,original_file,hash_file,verified) values (" + \
          data[0] + "," + data[1] + ",'" + data[2] + \
          "','" + hashlib.md5(open(imgdir + img,'r').read()).hexdigest() + ".jpg" + \
          "','N');\n"
    sqlf.write(sql)
sqlf.close()
