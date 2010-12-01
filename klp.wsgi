import web
import psycopg2
import decimal
import jsonpickle
import csv
import re
from web import form

# Needed to find the templates
import sys, os,traceback
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import Utility.KLPDB

urls = (
     '/','mainmap',
     '/pointinfo/', 'getPointInfo',
     '/assessment/(.*)/(.*)/(.*)','assessments',
     '/visualization*','visualization',
     '/info/school/(.*)','getSchoolInfo',
     '/info/preschool/(.*)','getSchoolInfo',
     '/shareyourstory(.*)\?*','shareyourstory',
     '/schoolpage/(.*)/(.*)','schoolpage',
     '/info/(.*)/(.*)','getBoundaryInfo',
     '/boundaryPoints/(.*)/(.*)','getBoundaryPoints',
     '/text/(.+)', 'text',
     '/schoolInfo/(.*)','getSchoolBoundaryInfo',
     '/insertsys/(.*)','insertSYS',
     '/postSYS/(.*)','postSYS',
     '/sysinfo','getSYSInfo',
)

connection = Utility.KLPDB.getConnection()
cursor = connection.cursor()

mySchoolform =form.Form(
                   form.Hidden('schoolid'),
                   form.Textbox('name'),
                   form.Textbox('email'),
                   form.Textbox('telephone'),
                   form.Textbox('dateofvisit'),
                   form.Radio('1',['Yes','No']),
                   form.Radio('2',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('3',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('4',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('5',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('6',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('7',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('8',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('9',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('10',['Available and functional', 'Available but not functional', 'Not available']),
                   form.Radio('11',['Yes','No']),
                   form.Textbox('12'),
                   form.Textbox('13'),
                   form.Textbox('14'),
                   form.Textbox('15'),
                   form.File('file1'),
                   form.File('file2'),
                   form.File('file3'),
                   form.File('file4'),
                   form.File('file5'),
                   form.Textarea('comments'))


myPreSchoolform =form.Form(
                   form.Hidden('schoolid'),
                   form.Textbox('name'),
                   form.Textbox('email'),
                   form.Textbox('telephone'),
                   form.Textbox('dateofvisit'),
                   form.Radio('16',['Yes','No','Do Not Know']),
                   form.Radio('17',['Yes','No','Do Not Know']),
                   form.Radio('18',['Yes','No','Do Not Know']),
                   form.Radio('19',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('20',['Yes','No','Do Not Know']),
                   form.Radio('21',['Yes','No','Do Not Know']),
                   form.Radio('22',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('23',['Yes','No','Do Not Know']),
                   form.Radio('24',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('25',['Yes','No','Do Not Know']),
                   form.Radio('26',['Yes','No','Do Not Know']),
                   form.Radio('27',['Yes','No','Do Not Know']),
                   form.Radio('28',['Yes','No','Do Not Know']),
                   form.Radio('29',['Yes','No','Do Not Know']),
                   form.Radio('30',['Yes','No','Do Not Know']),
                   form.Radio('31',['Yes','No','Do Not Know']),
                   form.Radio('32',['Yes','No','Do Not Know']),
                   form.Radio('33',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('34',['Yes','No','Do Not Know']),
                   form.Radio('35',['Yes','No','Do Not Know']),
                   form.Radio('36',['Yes','No','Do Not Know']),
                   form.Radio('37',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('38',['Available and used', 'Available but not used', 'Not available','Unknown']),
                   form.Radio('39',['Yes','No','Do Not Know']),
                   form.File('file1'),
                   form.File('file2'),
                   form.File('file3'),
                   form.File('file4'),
                   form.File('file5'),
                   form.Textarea('comments'))

baseassess = {"1":1,"2":3,"3":5,"4":7,"5":9,"6":13,"7":15,"8":19,"9":21,"10":23,"11":25,"12":26}

statements = {'get_district':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='District' and b.id=bcoord.id_bndry order by b.name",
              'get_preschooldistrict':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='PreSchoolDistrict' and b.id=bcoord.id_bndry order by b.name",
              'get_block':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='Block' and b.id=bcoord.id_bndry order by b.name",
              'get_cluster':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='Cluster' and b.id=bcoord.id_bndry order by b.name",
              'get_project':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='Project' and b.id=bcoord.id_bndry order by b.name",
              'get_circle':"select bcoord.id_bndry,ST_AsText(bcoord.coord),initcap(b.name) from vw_boundary_coord bcoord, tb_boundary b where bcoord.type='Circle' and b.id=bcoord.id_bndry order by b.name",
              'get_school':"select inst.instid ,ST_AsText(inst.coord),upper(s.name) from vw_inst_coord inst, tb_school s,tb_boundary b,tb_bhierarchy bhier where s.id=inst.instid and s.bid=b.id and bhier.id = b.hid and bhier.type='1' order by s.name",
              'get_preschool':"select inst.instid ,ST_AsText(inst.coord),upper(s.name) from vw_inst_coord inst, tb_school s,tb_boundary b,tb_bhierarchy bhier where s.id=inst.instid and s.bid=b.id and bhier.id = b.hid and bhier.type='2' order by s.name",
              'get_district_points':"select distinct b1.id, b1.name from tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy hier where b.id=b1.parent and b1.id=b2.parent and b.hid=hier.id and hier.type=1 and b.id=%s order by b1.name",
              'get_preschooldistrict_points':"select distinct b1.id, b1.name from tb_boundary b, tb_boundary b1,tb_boundary b2,tb_bhierarchy hier where b2.parent=b1.id and b1.parent = b.id and b.hid = hier.id and hier.type=2 and b.id=%s",
              'get_block_points':"select distinct b2.id, b2.name from tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy hier where b.id=b1.parent and b1.id=b2.parent  and b.hid = hier.id and hier.type=1 and b1.id=%s order by b2.name",
              'get_cluster_points':"select distinct s.id, s.name from tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id=b1.parent and b1.id=b2.parent and s.bid=b2.id and b.hid = hier.id and hier.type=1 and b2.id=%s order by s.name",
              'get_project_points':"select distinct b2.id, b2.name from tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy hier where b.id=b1.parent and b1.id=b2.parent  and b.hid = hier.id and hier.type=2 and b1.id=%s order by b2.name",
              'get_circle_points':"select distinct s.id, s.name from tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id=b1.parent and b1.id=b2.parent and s.bid=b2.id and b.hid = hier.id and hier.type=2 and b2.id=%s order by s.name",
              'get_district_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b.id = %s group by sv.sex",
              'get_district_info':"select count(distinct sv.id),b.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b.id = %s group by b.name",
              'get_preschooldistrict_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b.id = %s group by sv.sex",
              'get_preschooldistrict_info':"select count(distinct sv.id),b.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b.id = %s group by b.name",
              'get_block_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b1.id = %s group by sv.sex",
              'get_block_info':"select count(distinct sv.id),b1.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b1.id = %s group by b1.name",
              'get_project_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy bhier where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.hid=bhier.id and bhier.type='2' and b1.id = %s group by sv.sex",
              'get_project_info':"select count(distinct sv.id),b1.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy bhier where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.hid=bhier.id and bhier.type='2' and b1.id = %s group by b1.name",
              'get_cluster_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.id = %s group by sv.sex",
              'get_cluster_info':"select count(distinct sv.id),b2.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2 where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.id = %s group by b2.name",
              'get_circle_gender':"select sv.sex, sum(sv.num) from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy bhier where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.hid=bhier.id and bhier.type='2'and b2.id = %s group by sv.sex",
              'get_circle_info':"select count(distinct sv.id),b2.name from tb_school_agg sv, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_bhierarchy bhier where sv.bid = b2.id and b2.parent = b1.id and b1.parent = b.id and b2.hid=bhier.id and bhier.type='2' and b2.id = %s group by b2.name",
              'get_school_gender':"select sv.name, sv.sex, sum(sv.num) from tb_school_agg sv where sv.id = %s group by sv.name, sv.sex",
              'get_school_boundary_info':"select b.name, b1.name, b2.name, s.name,h.type from tb_boundary b, tb_boundary b1, tb_boundary b2, tb_school s,tb_bhierarchy h where s.id = %s and b.id=b1.parent and b1.id=b2.parent and s.bid=b2.id and b.hid=h.id",
              'get_num_stories':"select count(*) from tb_sys_data where schoolid= %s",
              'get_sys_school_questions':"select * from tb_sys_questions where hiertype=1 order by id",
              'get_sys_preschool_questions':"select * from tb_sys_questions where hiertype=2 order by id",
              'get_programme_info':"select p.name,p.start from tb_programme p where p.id =%s",
              'get_assessmentinfo':"select distinct p.name,p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg where agg.sid =%s  and ass.id = agg.assid and p.id = ass.pid",
              'get_district_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2, tb_school s,tb_bhierarchy hier where b.id=%s and b1.parent = b.id and b2.parent=b1.id and b.hid=hier.id and hier.type=1 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid",
              'get_block_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id = b1.parent and b1.id=b2.parent and b.hid=hier.id and hier.type=1 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid and b1.id=%s",
              'get_cluster_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id = b1.parent and b1.id=b2.parent and b.hid=hier.id and hier.type=1 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid and b2.id=%s",
              'get_preschooldistrict_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2, tb_school s,tb_bhierarchy hier where b.id=%s and b1.parent = b.id and b2.parent=b1.id and b.hid=hier.id and hier.type=2 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid",
              'get_project_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id = b1.parent and b1.id=b2.parent and b.hid=hier.id and hier.type=2 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid and b1.id=%s",
              'get_circle_assessmentinfo':"select distinct p.name, p.start,p.id from tb_programme p, tb_assessment ass, tb_school_assess_agg agg, tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s,tb_bhierarchy hier where b.id = b1.parent and b1.id=b2.parent and b.hid=hier.id and hier.type=2 and s.bid=b2.id and agg.sid = s.id and ass.id = agg.assid and p.id = ass.pid and b2.id=%s",
              'get_basic_assessmentinfo':"select agg.sex,s.name, sum(agg.aggval),b.id,b1.id,b2.id from tb_school_assess_agg agg,tb_assessment ass,tb_school s,tb_boundary b,tb_boundary b1, tb_boundary b2 where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s and s.id=agg.sid and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid group by agg.sex,s.name,b.id,b1.id,b2.id",
              'get_basic_district_assessmentinfo':"select agg.sex,b.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_school s,tb_boundary b,tb_boundary b1, tb_boundary b2 where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and ass.id=%s and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.sex,b.name",
              'get_basic_block_assessmentinfo':"select agg.sex,b1.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_school s,tb_boundary b,tb_boundary b1, tb_boundary b2 where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and ass.id=%s and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.sex,b1.name",
              'get_basic_cluster_assessmentinfo':"select agg.sex,b2.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_school s,tb_boundary b,tb_boundary b1, tb_boundary b2 where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and ass.id=%s and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.sex,b2.name",
              'get_basic_preschoolassessmentinfo':"select c.sex,s.name,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid and se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.id=%s group by c.sex,s.name",
              'get_basic_preschoolpreschooldistrict_assessmentinfo':"select c.sex,b.name,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1, tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid and se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent =b1.id and b1.parent=b.id and b.id=%s  group by c.sex,b.name",
              'get_basic_preschoolproject_assessmentinfo':"select c.sex,b1.name,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1, tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid and se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent =b1.id and b1.parent=b.id and b1.id=%s  group by c.sex,b1.name",
              'get_basic_preschoolcircle_assessmentinfo':"select c.sex,b2.name,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1, tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid and se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent =b1.id and b1.parent=b.id and b2.id=%s  group by c.sex,b2.name",
              'get_assessmentpertext':"select agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.aggtext",
              'get_district_assessmentpertext':"select agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.aggtext",
              'get_block_assessmentpertext':"select agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.aggtext",
              'get_cluster_assessmentpertext':"select agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.aggtext",
              'get_preschoolassessmentpertext':"select agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.aggtext",
              'get_preschoolpreschooldistrict_assessmentpertext':"select agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.aggtext",
              'get_preschoolproject_assessmentpertext':"select agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.aggtext",
              'get_preschoolcircle_assessmentpertext':"select agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.aggtext",
              'get_assessmentgender':"select agg.sex,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.sex,agg.aggtext",
              'get_district_assessmentgender':"select agg.sex,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.sex,agg.aggtext",
              'get_block_assessmentgender':"select agg.sex,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.sex,agg.aggtext",
              'get_cluster_assessmentgender':"select agg.sex,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.sex,agg.aggtext",
              'get_preschoolassessmentgender':"select agg.sex,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.sex,agg.aggtext",
              'get_preschoolpreschooldistrict_assessmentgender':"select agg.sex,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.sex,agg.aggtext",
              'get_preschoolproject_assessmentgender':"select agg.sex,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.sex,agg.aggtext",
              'get_preschoolcircle_assessmentgender':"select agg.sex,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.sex,agg.aggtext",
              'get_assessmentmt_count':"select agg.mt,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.mt",
              'get_district_assessmentmt_count':"select agg.mt,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.mt",
              'get_block_assessmentmt_count':"select agg.mt,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.mt",
              'get_cluster_assessmentmt_count':"select agg.mt,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.mt",
              'get_preschoolassessmentmt_count':"select c.mt,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid AND se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.id=%s group by c.mt",
              'get_preschoolpreschooldistrict_assessmentmt_count':"select c.mt,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid AND se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b.id=%s group by c.mt",
              'get_preschoolproject_assessmentmt_count':"select c.mt,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid AND se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b1.id=%s group by c.mt",
              'get_preschoolcircle_assessmentmt_count':"select c.mt,count(distinct stu.id) from tb_student stu, tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_child c,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id and stu.id = se.stuid AND se.assid = ass.id and ass.pid=%s and ass.id=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b2.id=%s group by c.mt",
              'get_assessmentmt':"select agg.mt,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.mt,agg.aggtext",
              'get_district_assessmentmt':"select agg.mt,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.mt,agg.aggtext",
              'get_block_assessmentmt':"select agg.mt,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.mt,agg.aggtext",
              'get_cluster_assessmentmt':"select agg.mt,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.mt,agg.aggtext",
              'get_preschoolassessmentmt':"select agg.mt,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s group by agg.mt,agg.aggtext",
              'get_preschoolpreschooldistrict_assessmentmt':"select agg.mt,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id  and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by agg.mt,agg.aggtext",
              'get_preschoolproject_assessmentmt':"select agg.mt,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id  and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by agg.mt,agg.aggtext",
              'get_preschoolcircle_assessmentmt':"select agg.mt,agg.aggtext, avg(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id  and ass.id=%s and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by agg.mt,agg.aggtext",
              'get_school_assessmentclass_count':"select cl.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s and cl.id=agg.clid group by cl.name",
              'get_school_assessmentclass':"select cl.name,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl where ass.pid=%s and agg.assid=ass.id and ass.id=%s and agg.sid=%s and cl.id=agg.clid group by cl.name,agg.aggtext",
              'get_district_assessmentclass_count':"select cl.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by cl.name",
              'get_district_assessmentclass':"select cl.name,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b.id=%s group by cl.name,agg.aggtext",
              'get_block_assessmentclass_count':"select cl.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by cl.name",
              'get_block_assessmentclass':"select cl.name,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b1.id=%s group by cl.name,agg.aggtext",
              'get_cluster_assessmentclass_count':"select cl.name, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by cl.name",
              'get_cluster_assessmentclass':"select cl.name,agg.aggtext, sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_class cl,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and ass.id=%s and cl.id=agg.clid and agg.sid=s.id and b.id=b1.parent and b1.id=b2.parent and b2.id=s.bid and b2.id=%s group by cl.name,agg.aggtext",
              'get_progress_count':"select ass.name,  sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass where ass.pid=%s and agg.assid=ass.id and agg.sid=%s group by ass.name,ass.start order by ass.start",
              'get_progress_countpreschool':"select ass.name,count(distinct stu.id), ass.start from tb_student stu,tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass where cl.sid = s.id and sc.clid = cl.id and sc.stuid=stu.id and stu.id =se.stuid and se.assid=ass.id and ass.pid=%s and sc.ayid=%s and s.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_preschool':"select s.name,agg.aggtext,ass.name,  avg(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_school s where ass.pid=%s and agg.assid=ass.id and agg.sid=%s and s.id=agg.sid group by s.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_school':"select s.name,agg.aggtext,ass.name,  sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_school s where ass.pid=%s and agg.assid=ass.id and agg.sid=%s and s.id = agg.sid group by s.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_district':"select ass.name,  sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_district':"select b.name,agg.aggtext,ass.name,   sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b.id = %s group by b.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_block':"select ass.name,  sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b1.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_block':"select b1.name,agg.aggtext,ass.name,   sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b1.id = %s group by b1.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_cluster':"select ass.name,  sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and agg.sid=s.id and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b2.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_cluster':"select b2.name,agg.aggtext,ass.name,   sum(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b2.id = %s group by b2.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_preschoolpreschooldistrict':"select ass.name,count(distinct stu.id), ass.start from tb_student stu,tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id and sc.clid = cl.id and sc.stuid=stu.id and stu.id =se.stuid and se.assid=ass.id and ass.pid=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_preschoolpreschooldistrict':"select b.name,agg.aggtext,ass.name,   avg(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b.id = %s group by b.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_preschoolproject':"select ass.name,count(distinct stu.id), ass.start from tb_student stu,tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id and sc.clid = cl.id and sc.stuid=stu.id and stu.id =se.stuid and se.assid=ass.id and ass.pid=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b1.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_preschoolproject':"select b1.name,agg.aggtext,ass.name,   avg(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b1.id = %s group by b1.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_progress_count_preschoolcircle':"select ass.name,count(distinct stu.id), ass.start from tb_student stu,tb_class cl, tb_student_class sc,tb_school s, tb_student_eval se, tb_assessment ass,tb_boundary b,tb_boundary b1,tb_boundary b2 where cl.sid = s.id and sc.clid = cl.id and sc.stuid=stu.id and stu.id =se.stuid and se.assid=ass.id and ass.pid=%s and sc.ayid=%s and s.bid=b2.id and b2.parent=b1.id and b1.parent=b.id and b2.id=%s group by ass.name,ass.start order by ass.start",
              'get_progress_preschoolcircle':"select b2.name,agg.aggtext,ass.name,   avg(agg.aggval),ass.start from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b2.id = %s group by b2.name,agg.aggtext,ass.name,ass.start order by ass.start",
              'get_assessmentinfo_district':"select b.name,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b.id = %s group by b.name",
              'get_assessmentinfo_block':"select b1.name,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b1.id = %s group by b1.name",
              'get_assessmentinfo_cluster':"select b2.name,sum(agg.aggval) from tb_school_assess_agg agg,tb_assessment ass,tb_boundary b, tb_boundary b1, tb_boundary b2,tb_school s where ass.pid=%s and agg.assid=ass.id and b.id=b1.parent and b1.id = b2.parent and s.bid = b2.id and agg.sid=s.id and b2.id = %s group by b2.name",
              'get_school_info':"select b.name, b1.name, b2.name, s.name,h.type,s.cat,s.sex,s.moi,s.mgmt,s.dise_code from tb_boundary b, tb_boundary b1, tb_boundary b2, tb_school s,tb_bhierarchy h where s.id = %s and b.id=b1.parent and b1.id=b2.parent and s.bid=b2.id and b.hid=h.id",
              'get_school_address_info':"select info.address,info.area,info.postcode,info.landmark_1,info.landmark_2,info.inst_id_1,info.inst_id_2, info.bus_no from tb_school_info info where info.schoolid=%s",
              'get_sys_info':"select sys.dateofvisit from tb_sys_data sys where sys.schoolid=%s group by sys.dateofvisit",
              'get_school_point':"select ST_AsText(inst.coord) from vw_inst_coord inst where inst.instid=%s",
              'get_sys_nums':"select count(*) from tb_sys_data",
              'get_sys_image_nums':"select count(*) from tb_sys_images",
              'get_school_images':"select hash_file from tb_sys_images where schoolid=%s and verified='Y'",
}
render = web.template.render('templates/', base='base')
render_plain = web.template.render('templates/')

application = web.application(urls,globals()).wsgifunc()


class mainmap:
  """Returns the main template"""
  def GET(self):
    web.header('Content-Type','text/html; charset=utf-8')
    return render.klp()

class getPointInfo:
  def GET(self):
    pointInfo={"district":[],"block":[],"cluster":[],"project":[],"circle":[],"preschooldistrict":[],"school":[],"preschool":[]}
    try:
      for type in pointInfo:
        cursor.execute(statements['get_'+type])
        result = cursor.fetchall()
        for row in result:
          try:
            match = re.match(r"POINT\((.*)\s(.*)\)",row[1])
          except:
            traceback.print_exc(file=sys.stderr)
            continue
          lon = match.group(1)
          lat = match.group(2)
          data={"lon":lon,"lat":lat,"name":row[2],"id":row[0]}
          pointInfo[type].append(data)
        connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    web.header('Content-Type', 'application/json')
    return jsonpickle.encode(pointInfo)


class visualization:
  def GET(self):
    web.header('Content-Type','text/html; charset=utf-8')
    return render.visualization()



class getSYSInfo:
  def GET(self):
    sysinfo={"numstories":0,"numimages":0}
    try:
      cursor.execute(statements['get_sys_nums'])
      result = cursor.fetchall()
      for row in result:
        sysinfo["numstories"]=int(row[0])
      cursor.execute(statements['get_sys_image_nums'])
      result = cursor.fetchall()
      for row in result:
        sysinfo["numimages"]=int(row[0])
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    web.header('Content-Type', 'application/json')
    return jsonpickle.encode(sysinfo)

    

class assessments:
  def GET(self,type,pid,id):
    data={}
    try:
      if pid == "1":
        assess = anganwadiAssessment(type,pid,id)
        data = assess.getData()
      elif pid == "2" or pid =="3" or pid=="4" or pid=="9" or pid=="10" or pid=="11":
        assess= nngAssessment(type,pid,id)
        data = assess.getData()
      elif pid =="5" or pid=="6" or pid=="7" or pid=="12":
        assess= readingAssessment(type,pid,id)
        data = assess.getData()
      elif pid=="8":
        assess= englishAssessment(type,pid,id)
        data = assess.getData()
      else:
        assess = baseAssessment(type,pid,id)
        data = assess.data
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    #print >> sys.stderr, data
    web.header('Content-Type','text/html; charset=utf-8')
    return render_plain.chart(data)


class baseAssessment:
    districtid=0
    blockid=0
    clusterid=0
    total=0
    count={}
    def __init__(self,type,programmeid,id):
      self.type = str(type)
      self.pid=programmeid
      self.id = id
      self.data= {"programme":{"pid":int(self.pid),"name":"","year":""},"type":self.type,"name":"","Boys":0,"Girls":0,"assessPerText":{},"baseline":{"gender":{},"mt":{},"class":{}},"progress":{},"analytics":[]}

    def getProgramInfo(self):
      try:
        cursor.execute(statements['get_programme_info'],(self.pid,))
        result = cursor.fetchall()
        for row in result:
          self.data["programme"]["name"]=row[0]
          self.data["programme"]["year"]=str(row[1]).split("-")[0]
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()
   
    def getBasicAssessmentInfo(self,type=""):
      try:
        if self.type in ('school','preschool'):
          query='get_basic_'+type+'assessmentinfo'
        else:
          query='get_basic_'+type+self.type+'_assessmentinfo'
        if type=='preschool':
          cursor.execute(statements[query],(self.pid,baseassess[self.pid],119,self.id,))
        else:
          #print >> sys.stderr, query
          cursor.execute(statements[query],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
          self.data["name"]=row[1].capitalize()
          if row[0] == "female":
            self.data["Girls"]=str(int(row[2]))
          if row[0] == "male":
            self.data["Boys"]=str(int(row[2]))
          self.total = self.total+row[2]
          self.count[row[0]]=row[2]
          if self.type=='school':
            self.districtid=row[3]
            self.blockid=row[4]
            self.clusterid=row[5]
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()

    def getBaselineGeneral(self,type=""):
      try:
        if self.type in ('school','preschool'):
          query='get_'+type+'assessmentpertext'
        else:
          query='get_'+type+self.type+'_assessmentpertext'
        cursor.execute(statements[query],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
          if row[1]==0:
            self.data["assessPerText"][row[0]]=0
          else:
            if type=="preschool":
              self.data["assessPerText"][row[0]]=float(row[1])*100.0
            else:
              self.data["assessPerText"][row[0]]=(float(row[1])/float(self.total))*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()

    def getBaselineGender(self,type=""):
      try:
        if self.type in ('school','preschool'):
          query='get_'+type+'assessmentgender'
        else:
          query='get_'+type+self.type+'_assessmentgender'
        cursor.execute(statements[query],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
          if row[0] =="female":
            gender="Girls"
          if row[0] =="male":
            gender="Boys"
          if not gender in self.data["baseline"]["gender"]:
            self.data["baseline"]["gender"][gender]={}
          if row[2]==0:
            self.data["baseline"]["gender"][gender][row[1]]=0
          else:
            if type=="preschool":
              self.data["baseline"]["gender"][gender][row[1]]=float(row[2])*100.0
            else:
              self.data["baseline"]["gender"][gender][row[1]]=(float(row[2])/float(self.count[row[0]]))*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()

    def getBaselineMTCount(self,type):
      if self.type in ('school'):
        query='get_'+type+'assessmentmt_count'
      else:
        query='get_'+type+self.type+'_assessmentmt_count'
      cursor.execute(statements[query],(self.pid,baseassess[self.pid],self.id,))
      result = cursor.fetchall()
      for row in result:
        self.count[row[0]]=row[1]

    def getBaselineMT(self,type=""):
      try:
        if type=="":
          self.getBaselineMTCount(type)
        if self.type in ('school','preschool'):
          query='get_'+type+'assessmentmt'
        else:
          query='get_'+type+self.type+'_assessmentmt'
        cursor.execute(statements[query],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
           if not row[0].capitalize() in self.data["baseline"]["mt"]:
              self.data["baseline"]["mt"][row[0].capitalize()]={}
           if row[2]==0:
             self.data["baseline"]["mt"][row[0].capitalize()][row[1]]=0
           else:
            if type=="preschool":
              self.data["baseline"]["mt"][row[0].capitalize()][row[1]]=float(row[2])*100.0
            else:
              self.data["baseline"]["mt"][row[0].capitalize()][row[1]]=(float(row[2])/float(self.count[row[0]]))*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()


    def getBaselineClass(self):
      try:
        cursor.execute(statements['get_'+self.type+'_assessmentclass_count'],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
          self.count[row[0]]=row[1]

        cursor.execute(statements['get_'+self.type+'_assessmentclass'],(self.pid,baseassess[self.pid],self.id,))
        result = cursor.fetchall()
        for row in result:
           std= "class-"+str(row[0])
           if not std in self.data["baseline"]["class"]:
              self.data["baseline"]["class"][std]={}
           if row[2]==0:
             self.data["baseline"]["class"][std][row[1]]=0
           else:
             self.data["baseline"]["class"][std][row[1]]=(float(row[2])/float(self.count[row[0]]))*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()


    def getProgressCount(self,type):
      if self.type in ('school'):
        query='get_progress_count'+type
      else:
        query='get_progress_count_'+type+self.type
      cursor.execute(statements[query],(self.pid,self.id,))
      result = cursor.fetchall()
      for row in result:
        self.count[row[0]]=row[1]


    def getProgressInfo(self,type=""):
      try:
        if type=="":
          self.getProgressCount(type)
        if self.type in ('school','preschool'):
          query='get_progress_'+self.type
        else:
          query='get_progress_'+type+self.type

        cursor.execute(statements[query],(self.pid,self.id,))
        result = cursor.fetchall()
        for row in result:
           if not row[1] in self.data["progress"]:
              self.data["progress"][row[1]]={}
           if row[3]==0:
             self.data["progress"][row[1]][row[2]]=0
           else:
             if type=="preschool":
               self.data["progress"][row[1]][row[2]]=float(row[3])*100.0
             else:
               self.data["progress"][row[1]][row[2]]=(float(row[3])/float(self.count[row[2]]))*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()
    
    def getAnalyticsInfo(self):   
      temp={}
      timeArray=[]

      name=self.data["name"].capitalize()+" (School)"
      try:
        cursor.execute(statements['get_progress_school'],(self.pid,self.id,))
        result = cursor.fetchall()
        for row in result:
          if not row[2] in temp:
            temp[row[2]]={}
            timeArray.append(row[2])
          if not name in temp[row[2]]:
            temp[row[2]][name]={}
          if row[3]==0:
            temp[row[2]][name][row[1]]=0
          else:
            temp[row[2]][name][row[1]]=(float(row[3])/float(self.total))*100.0


        boundaries={"district":self.districtid,"block":self.blockid,"cluster":self.clusterid}

        for boundary in boundaries:
          cursor.execute(statements['get_assessmentinfo_'+boundary],(self.pid,boundaries[boundary],))
          result = cursor.fetchall()
          for row in result:
            boundarytotal=row[1]

          cursor.execute(statements['get_progress_'+boundary],(self.pid,boundaries[boundary],))
          result = cursor.fetchall()
          for row in result:
            bname=row[0].capitalize()+" ("+boundary.capitalize()+")"
            if not row[2] in temp:
              temp[row[2]]={}
            if not bname in temp[row[2]]:
              temp[row[2]][bname]={}
            if row[3]==0:
              temp[row[2]][bname][row[1]]=0
            else:
              temp[row[2]][bname][row[1]]=(float(row[3])/float(boundarytotal))*100.0

        for i in timeArray:
          self.data["analytics"].append({i:temp[i]})
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()


class anganwadiAssessment(baseAssessment):

    def getProgressInfo(self,type=""):
      try:
        if self.type in ('school','preschool'):
          query='get_progress_'+self.type
        else:
          query='get_progress_'+type+self.type
        cursor.execute(statements[query],(self.pid,self.id,))
        result = cursor.fetchall()
        for row in result:
           if not row[2] in self.data["progress"]:
              self.data["progress"][row[2]]={}
           if row[3]==0:
             self.data["progress"][row[2]][row[1]]=0
           else:
             self.data["progress"][row[2]][row[1]]=float(row[3])*100.0
      except:
        traceback.print_exc(file=sys.stderr)
        connection.rollback()

    def getBaselineAssessmentInfo(self):
      self.getBaselineGeneral("preschool")
      self.getBaselineGender("preschool")
      self.getBaselineMT("preschool")

    def getData(self):
      self.getProgramInfo()
      self.getBasicAssessmentInfo("preschool")
      self.getBaselineAssessmentInfo()
      self.getProgressInfo("preschool")
      connection.commit()
      return self.data

class nngAssessment(baseAssessment):
    def getBaselineAssessmentInfo(self):
      self.getBaselineGeneral()
      self.getBaselineGender()
      self.getBaselineMT()
      self.getBaselineClass()

    def getData(self):
      self.getProgramInfo()
      self.getBasicAssessmentInfo()
      self.getBaselineAssessmentInfo()
      self.getProgressInfo()
      if self.type =="school":
        self.getAnalyticsInfo()
      connection.commit()
      return self.data


class readingAssessment(baseAssessment):
    def getBaselineAssessmentInfo(self):
      self.getBaselineGeneral()
      self.getBaselineGender()
      self.getBaselineMT()
      self.getBaselineClass()

    def getData(self):
      self.getProgramInfo()
      self.getBasicAssessmentInfo()
      self.getBaselineAssessmentInfo()
      self.getProgressInfo()
      if self.type =="school":
        self.getAnalyticsInfo()
      connection.commit()
      return self.data


class englishAssessment(baseAssessment):
    def getBaselineAssessmentInfo(self):
      self.getBaselineGeneral()
      self.getBaselineGender()
      self.getBaselineMT()
      self.getBaselineClass()

    def getData(self):
      self.getProgramInfo()
      self.getBasicAssessmentInfo()
      self.getBaselineAssessmentInfo()
      self.getProgressInfo()
      if self.type =="school":
        self.getAnalyticsInfo()
      connection.commit()
      return self.data

class schoolpage:
  def GET(self,type,id):
    data={'name':'','type':'','id':'','sysdate':[]}
    data["type"]=str(type)
    data["id"]=int(id)
    try:
      cursor.execute(statements['get_school_info'],(id,))
      result = cursor.fetchall()
      for row in result:
        data["b"]=row[0].capitalize()
        data["b1"]=row[1].capitalize()
        data["b2"]=row[2].capitalize()
        data["name"]=row[3].capitalize()
        if row[4]==None:
          data["type"]='-'
        else:
          data["type"]=row[4]
        if row[5]==None:
          data["cat"]='-'
        else:
          data["cat"]=row[5].upper()
        if row[6]==None:
          data["sex"]='-'
        else:
          data["sex"]=row[6].capitalize()
        if row[7]==None:
          data["moi"]='-'
        else:
          data["moi"]=row[7].capitalize()
        if row[8]==None:
          data["mgmt"]='-'
        else:
          data["mgmt"]=row[8].capitalize()
        if row[9]==None:
          data["dise_code"]='-'
        else:
          data["dise_code"]=row[9]
      cursor.execute(statements['get_school_address_info'],(id,))
      result = cursor.fetchall()
      data["address"]='-'
      for row in result:
        data["address"]=row[0]
        data["area"]=row[1]
        data["postcode"]=row[2]
        data["landmark_1"]=row[3]
        data["landmark_2"]=row[4]
        data["inst_id_1"]=row[5]
        data["inst_id_2"]=row[6]
        data["bus_no"]=row[7]

      #Added to query images from tb_sys_images
      from ConfigParser import SafeConfigParser
      config = SafeConfigParser()
      config.read(os.path.join(os.getcwd(),'config/klpconfig.ini'))
      imgpath = config.get('Pictures','hashpicpath')
      data["image_dir"] = "/" + imgpath
      cursor.execute(statements['get_school_images'],(id,))
      result = cursor.fetchall()
      data["images"]=[]
      for row in result:
        data["images"].append(row[0])

      cursor.execute(statements['get_school_gender'],(id,))
      result = cursor.fetchall()
      for row in result:
        if row[1] == "female":
          data["numGirls"]=int(row[2])
        if row[1] == "male":
          data["numBoys"]=int(row[2])

      data["numStudents"]= data["numBoys"]+data["numGirls"]

      cursor.execute(statements['get_sys_info'],(id,))
      result = cursor.fetchall()
      data["syscount"]=0
      for row in result:
        data["syscount"]=data["syscount"]+1
        if row[0]==None:
          data["sysdate"].append('')
        else:
          data["sysdate"].append(str(row[0]))

      cursor.execute(statements['get_school_point'],(id,))
      result = cursor.fetchall()
      for row in result:
        match = re.match(r"POINT\((.*)\s(.*)\)",row[0])
        data["lon"] = match.group(1)
        data["lat"] = match.group(2)
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()

    print >> sys.stderr, data
    web.header('Content-Type','text/html; charset=utf-8')
    return render_plain.schoolpage(data)

class shareyourstory:
  def GET(self,type):
    questions=[]
    try:
      cursor.execute(statements['get_sys_'+type+'_questions'])
      result = cursor.fetchall()
      for row in result:
        questions.append({"id":row[0],"text":row[2],"field":row[3],"type":row[4],"options":row[5]})
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    web.header('Content-Type','text/html; charset=utf-8')
    return render_plain.shareyourstory(questions)

class text:
  def GET(self, name):
    web.header('Content-Type','text/html; charset=utf-8')
    textlinks = {'library': 'library', 'maths': 'maths', 'preschool': 'preschool', 'reading': 'reading', 'partners': 'partners','aboutus':'aboutus','credits':'credits'}

    try:
      return eval('render.' + textlinks[name] + '()')
    except KeyError:
      return web.badrequest()

class getBoundaryInfo:
  def GET(self,type,id):
    boundaryInfo ={}
    boundaryInfo["id"]=id
    boundaryInfo["numBoys"]=0
    boundaryInfo["numGirls"]=0
    boundaryInfo["numSchools"]=0
    boundaryInfo["assessments"]=""

    try:
      cursor.execute(statements['get_'+type+'_assessmentinfo'],(id,))
      result = cursor.fetchall()
      assessments= ""
      first=1
      for row in result:
        if first: 
          assessments=assessments+row[0]+"-"+str(row[1]).split("-")[0]+","+str(row[2])
          first=0
        else:
          assessments=assessments+";"+row[0]+"-"+str(row[1]).split("-")[0]+","+str(row[2])
      boundaryInfo["assessments"]=str(assessments)
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()

    try:
      cursor.execute(statements['get_'+type+'_info'],(id,))
      result = cursor.fetchall()
      for row in result:
        boundaryInfo["numSchools"]=str(row[0])
        boundaryInfo["name"]=str(row[1])
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
   
    try:
      cursor.execute(statements['get_'+type+'_gender'],(id,))
      result = cursor.fetchall()
      for row in result:
        if row[0] == "female":
          boundaryInfo["numGirls"]=row[1]
        if row[0] == "male":
          boundaryInfo["numBoys"]=row[1]
      boundaryInfo["numStudents"]= boundaryInfo["numBoys"]+boundaryInfo["numGirls"]
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    connection.commit()
    web.header('Content-Type', 'application/json')
    return jsonpickle.encode(boundaryInfo)

class getSchoolInfo:
  def GET(self,id):
    schoolInfo={}
    schoolInfo["id"]=id
    schoolInfo["numStories"]=0
    schoolInfo["numBoys"]=0
    schoolInfo["numGirls"]=0
    schoolInfo["numStudents"]=0
    schoolInfo["assessments"]=""
    encodedschoolInfo=""

    try:
      cursor.execute(statements['get_assessmentinfo'],(id,))
      result = cursor.fetchall()
      assessments= ""
      first=1
      for row in result:
        if first:
          assessments=assessments+row[0]+"-"+str(row[1]).split("-")[0]+","+str(row[2])
          first=0
        else:
          assessments=assessments+";"+row[0]+"-"+str(row[1]).split("-")[0]+","+str(row[2])
      schoolInfo["assessments"]=assessments.decode('utf-8')
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()

    try:
      cursor.execute(statements['get_school_gender'],(id,))
      result = cursor.fetchall()
      for row in result:
        schoolInfo["name"]=row[0]
        if row[1] == "female":
          schoolInfo["numGirls"]=row[2]
        if row[1] == "male":
          schoolInfo["numBoys"]=row[2]

      schoolInfo["numStudents"]= schoolInfo["numBoys"]+schoolInfo["numGirls"]
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    
    try:
      cursor.execute(statements['get_num_stories'],(id,))
      result = cursor.fetchall()
      for row in result:
        schoolInfo["numStories"]=row[0]
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    connection.commit()
    web.header('Content-Type', 'application/json; charset=utf-8')
    return jsonpickle.encode(schoolInfo)


class getBoundaryPoints: 
  def GET(self,type,id):
    boundaryInfo =[]
    try:
      cursor.execute(statements['get_'+type+'_points'],(id,))
      result = cursor.fetchall()
      for row in result:
        data={"id":row[0],"name":row[1].capitalize()}
        boundaryInfo.append(data)
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    web.header('Content-Type', 'application/json')
    return jsonpickle.encode(boundaryInfo)
 
class getSchoolBoundaryInfo:
  def GET(self,id):
    schoolInfo = {"district":"","block":"","cluster":"","schoolname":"","type":""}
    try:
      cursor.execute(statements['get_school_boundary_info'],(id,))
      result = cursor.fetchall()
      for row in result:
        schoolInfo ={"district":row[0].capitalize(),"block":row[1].capitalize(),"cluster":row[2].capitalize(),"schoolname":row[3].capitalize(),"type":row[4]}
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
    web.header('Content-Type', 'application/json')
    return jsonpickle.encode(schoolInfo)

class insertSYS:
  def GET(self,query):
    try:
      cursor.execute(query)
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()


class postSYS:

  def populateImages(self,selectedfile,schoolid,sysid):
      #Getting path to picture files from the config file
      from ConfigParser import SafeConfigParser
      import hashlib
      config = SafeConfigParser()
      config.read(os.path.join(os.getcwd(),'config/klpconfig.ini'))
      savepath = config.get('Pictures','origpicpath')
      if selectedfile.filename != "":
        try:
          if(os.path.exists(savepath+selectedfile.filename)):
            savefilename = selectedfile.filename.split('.')[0] + '-' + schoolid + '.jpg'
          else:
            savefilename = selectedfile.filename
            wf=open(savepath + savefilename,'w')
            wf.write(selectedfile.file.read())
            wf.close()
            hashed_filename = hashlib.md5(open(savepath +savefilename,'r').read()).hexdigest() + '.jpg'
        except IOError:
          traceback.print_exc(file=sys.stderr)
          print "Error occurred during processing this file: " + savefilename
        imagequery = "insert into tb_sys_images(schoolid,original_file,hash_file,sysid,verified) values( %s , %s, %s, %s, %s)"
        try:
          cursor.execute(imagequery,(schoolid,savefilename,hashed_filename,sysid,'N')) #Images coming in from this flow are yet to be verified
          connection.commit()
        except:
          traceback.print_exc(file=sys.stderr)
          connection.rollback()

  def POST(self,type):
    try:
      schoolid=0
      if type=="school":
        form = mySchoolform()
        #print >> sys.stderr, "Type is school"
      else:
        form = myPreSchoolform()
        #print >> sys.stderr, "Type is preschool :"+type
      if not form.validates(): 
         for k in form.inputs: 
           return "id = ", k.id
      count=0

      query="insert into tb_sys_data"
      qansquery = "insert into tb_sys_qans(sysid,qid,answer) values( %(sysid)s,%(qid)s,%(answer)s)"
      data={}
      qdata={}
      for k in form.inputs: 
        if not(k.id.startswith('file')) and k.value != '' and k.value != None:
          if k.id in ('schoolid','name','email','telephone','dateofvisit','comments'):
            data[k.id]=k.value
          else:
            qdata[k.id]=k.value

      fields = ', '.join(data.keys())
      values = ', '.join(['%%(%s)s' % x for x in data])
      query=query+"("+fields+") values("+values+")"
      #print >> sys.stderr, str(query)
      #print >> sys.stderr, "Questions:-"+str(qdata)
      #return query+" Data:"+str(data)
      cursor.execute("BEGIN")
      cursor.execute("LOCK TABLE tb_sys_data IN ROW EXCLUSIVE MODE");
      cursor.execute(query,data)
      cursor.execute("select nextval('tb_sys_data_id_seq')")
      result = cursor.fetchall()
      cursor.execute("COMMIT")
      for row in result:
        sysid=row[0]-1
      for q in qdata.keys():
        cursor.execute(qansquery,{'sysid':sysid,'qid':q,'answer':qdata[q]})
      connection.commit()
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()
   
    #add photos
    try:
      schoolid= form['schoolid'].value
      x = web.input(file1={})
      self.populateImages(x.file1,schoolid,sysid)
      x = web.input(file2={})
      self.populateImages(x.file2,schoolid,sysid)
      x = web.input(file3={})
      self.populateImages(x.file3,schoolid,sysid)
      x = web.input(file4={})
      self.populateImages(x.file4,schoolid,sysid)
      x = web.input(file5={})
      self.populateImages(x.file5,schoolid,sysid)
    except:
      traceback.print_exc(file=sys.stderr)
      connection.rollback()

    web.header('Content-Type','text/html; charset=utf-8')
    return render_plain.sys_submitted()
   

