-- Schema creation script for KLP aggregate DB
-- This DB drives the KLP website
-- Created: Mon, 07 Jun 2010 13:32:23 IST
-- (C) Alok G Singh <alok@klp.org.in>

-- This code is released under the terms of the GNU GPL v3 
-- and is free software

DROP TABLE IF EXISTS "tb_bhierarchy" cascade;
CREATE TABLE "tb_bhierarchy" (
  "id" integer unique, -- 'Hierarchy id'
  "type" integer, -- 'Hierarchy type id'
  "parent" integer default NULL,
  "name" varchar(300) NOT NULL,
  PRIMARY KEY  ("id")
);

DROP TABLE IF EXISTS "tb_boundary" cascade;
CREATE TABLE "tb_boundary" (
  "id" integer unique, -- 'Boundary id'
  "parent" integer default NULL,
  "name" varchar(300) NOT NULL,
  "hid" integer NOT NULL references "tb_bhierarchy" ("id") on delete cascade,
  PRIMARY KEY  ("id")
);

DROP TABLE IF EXISTS "tb_address" cascade;
CREATE TABLE "tb_address" (
  "id" integer unique, -- 'Address id'
  "address" varchar(1000) default NULL,
  "landmark" varchar(1000) default NULL,
  "pin" varchar(20) default NULL,
  PRIMARY KEY ("id")
);

DROP TYPE IF EXISTS school_category cascade;
CREATE TYPE school_category as enum('Model Primary', 'Anganwadi', 'Akshara Balwadi', 'Independent  Balwadi', 'Others', 'Lower Primary', 'Upper Primary', 'Secondary');
DROP TYPE IF EXISTS school_sex cascade;
CREATE TYPE school_sex as enum('boys','girls','co-ed');
DROP TYPE IF EXISTS sex cascade;
CREATE TYPE sex as enum('male','female');
DROP TYPE IF EXISTS school_moi cascade;
CREATE TYPE school_moi as enum('kannada','urdu','tamil','telugu','english','marathi','malayalam', 'hindi', 'konkani', 'sanskrit', 'sindhi', 'other', 'gujarathi', 'not known', 'english and marathi', 'multi lng', 'nepali', 'oriya', 'bengali', 'english and hindi', 'english, telugu and urdu');  -- 'Medium of instruction
DROP TYPE IF EXISTS school_management cascade;
CREATE TYPE school_management as enum('ed', 'swd', 'local', 'p-a', 'p-ua', 'others', 'approved', 'ssa', 'kgbv', 'p-a-sc', 'p-a-st', 'jawahar', 'central', 'sainik', 'central govt', 'nri', 'madrasa-a', 'madrasa-ua', 'arabic-a', 'arabic-ua', 'sanskrit-a', 'sanskrit-ua', 'p-ua-sc', 'p-ua-st');


DROP TABLE IF EXISTS "tb_school" cascade;
CREATE TABLE "tb_school" (
  "id" integer unique, -- 'School id'
  "bid" integer NOT NULL REFERENCES "tb_boundary" ("id") ON DELETE CASCADE, -- 'Lowest Boundary id'
  "aid" integer default NULL REFERENCES "tb_address" ("id") ON DELETE CASCADE, -- 'Address id'
  "dise_code" varchar(14) default NULL,
  "name" varchar(300) NOT NULL,
  "cat" school_category default NULL,
  "status" integer NOT NULL, -- '0 is Inactive, 1 is Active'
  "sex" school_sex default 'co-ed',
  "moi" school_moi default 'kannada',
  "mgmt" school_management default 'ed',
  PRIMARY KEY  ("id")
);

DROP TABLE IF EXISTS "tb_child" cascade;
CREATE TABLE "tb_child" (
  "id" integer unique, -- 'School id'
  "name" varchar(300) NOT NULL,
  "dob" date default NULL,
  "sex" sex NOT NULL default 'male',
  "mt" school_moi default 'kannada', -- Mother tongue
  PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "tb_class" cascade;
CREATE TABLE "tb_class" (
  "id" integer unique, -- 'Class id'
  "sid" integer, -- School id
  "name" integer NOT NULL,
  "section" char(1) default NULL,
  PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "tb_academic_year" cascade;
CREATE TABLE "tb_academic_year" (
  "id" integer unique, -- 'Academic year id'
  "name" varchar(20),
  PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "tb_student" cascade;
CREATE TABLE "tb_student" (
  "id" integer unique, -- 'Student id'
  "clid" integer NOT NULL REFERENCES "tb_class" ("id") ON DELETE CASCADE, -- 'Class id'
  "cid" integer NOT NULL REFERENCES "tb_child" ("id") ON DELETE CASCADE, -- 'Child id'
  PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "tb_student_class" cascade;
CREATE TABLE "tb_student_class" (
  "stuid" integer NOT NULL REFERENCES "tb_student" ("id") ON DELETE CASCADE, -- 'Student id'
  "clid" integer NOT NULL REFERENCES "tb_class" ("id") ON DELETE CASCADE, -- 'Class id'
  "ayid" integer NOT NULL REFERENCES "tb_academic_year" ("id") ON DELETE CASCADE,
  "status" integer NOT NULL
);

DROP TABLE IF EXISTS "tb_programme" cascade;
CREATE TABLE "tb_programme" (
  "id" serial unique, -- 'Programme id'
  "name" varchar(300) NOT NULL,
  "start" date default CURRENT_DATE,
  "end" date default CURRENT_DATE,
  PRIMARY KEY ("id")
);

-- Seed data
insert into tb_programme values (default, 'Anganwadi', '2009-06-01', '2020-05-31'),
                                (default, 'NNG', '2007-06-01', '2008-05-31'),
                                (default, 'NNG', '2008-06-01', '2009-05-31'),
                                (default, 'NNG3', '2009-06-01', '2010-05-31'),
                                (default, 'Reading', '2006-06-01', '2007-05-31'),
                                (default, 'Reading', '2008-06-01', '2009-05-31'),
                                (default, 'Reading', '2009-06-01', '2010-05-31'),
                                (default, 'English', '2009-06-01', '2010-05-31'),
                                (default, 'Ramanagara-NNG1', '2009-06-01', '2010-05-31'),
                                (default, 'Ramanagara-NNG2', '2009-06-01', '2010-05-31'),
                                (default, 'Target NNG', '2009-06-01', '2010-05-31'),
                                (default, 'Target Reading', '2009-06-01', '2010-05-31');

DROP TABLE IF EXISTS "tb_assessment" cascade;
CREATE TABLE "tb_assessment" (
  "id" serial unique, -- 'Assessment id'
  "name" varchar(300) NOT NULL,
  "pid" integer references "tb_programme" ("id") ON DELETE CASCADE, -- Programme id
  "start" date default CURRENT_DATE,
  "end" date default CURRENT_DATE,
  PRIMARY KEY ("id")
);

-- Seed data 
-- 2009 Anganwadi
insert into tb_assessment values (default, 'Pre test', 1, '2009-10-1', '2009-12-01'), --1
                                 (default, 'Post test', 1, '2010-01-1', '2010-02-01'); --2
-- 2007 NNG
insert into tb_assessment values (default, '20th day test', 2, '2007-10-1', '2007-02-01'), --3
                                 (default, '60th day test', 2, '2008-01-1', '2008-02-01'); --4
-- 2008 NNG
insert into tb_assessment values (default, '20th day test', 3, '2008-10-1', '2008-02-01'), --5
                                 (default, '60th day test', 3, '2009-01-1', '2009-02-01'); --6
-- 2009 NNG3
insert into tb_assessment values (default, 'Pre test', 4, '2009-10-1', '2009-12-01'), --7
                                 (default, 'Post test', 4, '2010-01-1', '2010-02-01'); --8
-- 2006 Reading
insert into tb_assessment values (default, 'Baseline', 5, '2006-07-1', '2006-08-01'), --9
                                 (default, '15th day test', 5, '2006-09-1', '2006-10-01'), --10
                                 (default, '30th day test', 5, '2006-10-1', '2006-11-01'), --11
                                 (default, '45th day test', 5, '2006-11-1', '2006-12-01'); --12
-- 2008 11 districts (ಪರಿಹರ ಬೊಧನೆ, Reading)
insert into tb_assessment values (default, 'Pre test', 6, '2008-10-1', '2009-12-01'), --13
                                 (default, 'Post test', 6, '2009-01-1', '2009-02-01'); --14
-- 2009 Reading
insert into tb_assessment values (default, 'Pre test', 7, '2009-10-1', '2009-11-01'), --15
                                 (default, 'Post test', 7, '2010-01-1', '2010-02-01'), --16
                                 (default, 'Mid test', 7, '2009-11-1', '2009-12-01'), --17
                                 (default, '20th day', 7, '2009-11-1', '2009-12-01'); --18
-- 2009 English
insert into tb_assessment values (default, 'Pre test', 8, '2009-10-1', '2009-12-01'), --19
                                 (default, 'Post test', 8, '2010-01-1', '2010-02-01'); --20
-- 2009 Ramanagara NNG1
insert into tb_assessment values (default, 'Pre test', 9, '2009-10-1', '2009-12-01'), --21
                                 (default, 'Post test', 9, '2010-01-1', '2010-02-01'); --22
-- 2009 Ramanagara NNG2
insert into tb_assessment values (default, 'Pre test', 10, '2009-10-1', '2009-12-01'), --23
                                 (default, 'Post test',10, '2010-01-1', '2010-02-01'); --24
-- 2009 Target NNG
insert into tb_assessment values (default, 'NNG2', 11, '2010-01-1', '2010-02-01'); --25
-- 2009 Target Reading
insert into tb_assessment values (default, 'Reading', 12, '2010-01-1', '2010-02-01'); --26

DROP TABLE IF EXISTS "tb_question" cascade;
CREATE TABLE "tb_question" (
  "id" integer, -- 'Question id'
  "assid" integer references "tb_assessment" ("id") ON DELETE CASCADE, -- Assessment id
  "desc" varchar(100) NOT NULL,
  PRIMARY KEY ("id", "assid")
);

DROP TABLE IF EXISTS "tb_student_eval" cascade;
CREATE TABLE "tb_student_eval" (
  "qid" integer,-- references "tb_question" ("id") ON DELETE CASCADE, -- 'Question id'
  "assid" integer references "tb_assessment" ("id") ON DELETE CASCADE, -- Assessment id
  "stuid" integer references "tb_student" ("id") ON DELETE CASCADE, -- Student id
  "mark" numeric(5,2) default NULL,
  "grade" char(2) default NULL,
  "ayid" integer NOT NULL REFERENCES "tb_academic_year" ("id") ON DELETE CASCADE,
  PRIMARY KEY ("qid", "assid", "stuid")
);


DROP TABLE IF EXISTS "tb_sys_data" cascade;
CREATE TABLE "tb_sys_data" (
  "id" serial unique, -- 'SYS id'
  "schoolid" integer NOT NULL references "tb_school" ("id") on delete cascade,
  "name" varchar(100),
  "email" varchar(100),
  "telephone" varchar(50),
  "dateofvisit" varchar(50),
  "comments" varchar(500),
  "entered_timestamp" timestamp with time zone not null default now() 
);


DROP TABLE IF EXISTS "tb_sys_qans";
CREATE TABLE "tb_sys_qans"(
  "sysid" integer NOT NULL references "tb_sys_data" ("id") on delete cascade,
  "qid" integer,
  "answer" varchar(500)
);

DROP TYPE IF EXISTS sys_question_type;
CREATE TYPE sys_question_type as enum('text', 'numeric', 'radio');

DROP TABLE IF EXISTS "tb_sys_questions";
CREATE TABLE "tb_sys_questions" (
  "id" serial unique, -- 'Question id'
  "hiertype" integer, -- 1 for school, 2 for preschool
  "qtext" varchar(500),
  "qfield" varchar(50),
  "qtype" sys_question_type,
  "options" varchar(100)[]
);

--Seed data for school questions
INSERT INTO tb_sys_questions values(default,1,'Is the school building an all weather (pucca) building?','schoolq1','radio','{"Yes","No"}');
INSERT INTO tb_sys_questions values(default,1,'Does the school have boundary wall / fencing for security?','schoolq2','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Does the school have a playground?','schoolq3','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Is the school building suitable for access by children with disability (barrier free access etc.)?','schoolq4','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Is there a separate room for Headmaster''s office (which can also be used as a store room)?','schoolq5','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Is there a separate room for kitchen / store for mid day meals?','schoolq6','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Are there separate toilets for boys and girls ?','schoolq7','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Does the school have safe and adequate drinking water facility?','schoolq8','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Does the school have a  library?','schoolq9','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Does the school have any play material / sports equipment?','schoolq10','radio','{"Available and functional", "Available but not functional", "Not available"}');
INSERT INTO tb_sys_questions values(default,1,'Did you see any evidence of mid day meal being served (food being cooked, food waste etc.) on the day of your visit?','schoolq11','radio','{"Yes","No"}');
INSERT INTO tb_sys_questions values(default,1,'How many functional class rooms (exclude rooms that are not used for conducting classes for whatever reason) does the school have?','schoolq12','text');
INSERT INTO tb_sys_questions values(default,1,'How many classrooms had multiple teachers sharing  a classroom?','schoolq13','text');
INSERT INTO tb_sys_questions values(default,1,'How many classrooms had no teachers in the class?','schoolq14','text');
INSERT INTO tb_sys_questions values(default,1,'What was the total numbers of teachers present (including head master)?','schoolq15','text');

--Seed data for anganwadi sys
INSERT INTO tb_sys_questions values(default,2,'Did the anganwadi open as per the prescribed time on the day of your visit (10 AM)?','angq1','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is the anganwadi run in its own building (designated for running Anganwadi) built by the Woman & Child department?','angq2','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Were at least 50% of the children enrolled were present on the day of visit?','angq3','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Does the  anganwadi worker maintain a register of children’s attendance?','angq4','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'Did the Anganwadi seem spacious enough for the number of children that were there?','angq5','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is there is enough space available for children to play in the Anganwadi premise?','angq6','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is there a separate corner designated for stocking food in the Anganwadi premises?','angq7','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'If this space to stock food was observed, was this space  neat and free from dust, waste and protected from rain and wind and free from pest, worms and rats?','angq8','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Was the prepared food covered and hygienically stored?','angq9','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'Did all children received their food, on-time, time on the day of your visit?','angq10','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is the floor of the anganwadi well maintained and free of damage? ','angq11','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is the roof of the anganwadi well maintained and free of damage and leaks? ','angq12','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Are the doors and windows of the anganwadi strong and can they be bolted and locked?','angq13','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Are the walls of the anganwadi painted?','angq14','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Do the children use waste basket and was it clean?','angq15','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Was clean drinking water stored in clean vessels?','angq16','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Was the an arrangement made for children to wash hands after eating?','angq17','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is there a toilet in usable condition?','angq18','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'Is the teacher trained  to teach physically challenged / disabled children?','angq19','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Are Bal Vikas Samithi meetings held as per the norm?','angq20','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Is there a Friends of Anganwadi group for this anganwadi?','angq21','radio','{"Yes","No","Do Not Know"}');
INSERT INTO tb_sys_questions values(default,2,'Does the anganwadi have a black board and is it being used?','angq22','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'Does the preschool have enough teaching and learning materials to keep the children engaged?','angq23','radio','{"Available and used", "Available but not used","Not available","Unknown"}');
INSERT INTO tb_sys_questions values(default,2,'Are the children using the play materials in the preschool?','angq24','radio','{"Yes","No","Do Not Know"}');

DROP TABLE IF EXISTS "tb_sys_images";
CREATE TABLE "tb_sys_images" (
  "schoolid" integer,
  "original_file" varchar(100),
  "hash_file" varchar(100),
  "verified" varchar(1),
  "sysid" integer NOT NULL references "tb_sys_data" ("id") on delete cascade
);

DROP TABLE IF EXISTS "tb_school_info";
CREATE TABLE "tb_school_info"(
  "schoolid" integer NOT NULL references "tb_school" ("id") on delete cascade,
  "address" varchar(255),
  "area" varchar(100),
  "postcode" varchar(100),
  "landmark_1" varchar (100),
  "landmark_2" varchar (100),
  "inst_id_1" varchar (100),
  "inst_id_2" varchar (100),
  "bus_no" varchar (100),
  "mp" varchar(100),
  "mla" varchar(100),
  "ward" varchar(100),
  PRIMARY KEY  ("schoolid")
);
-- Remote views via dblink

CREATE OR REPLACE VIEW vw_boundary_coord as 
       select * from dblink('host=localhost dbname=klp-coord user=klp password=1q2w3e4r', 'select * from boundary_coord') 
       as t1 (id_bndry integer, 
              type varchar(20), 
              coord geometry);

CREATE OR REPLACE VIEW vw_inst_coord as
       select * from dblink('host=localhost dbname=klp-coord user=klp password=1q2w3e4r', 'select * from inst_coord') 
       as t2 (instid integer,
              coord geometry);

-- The web user will query the DB
GRANT SELECT ON tb_school, 
                tb_student, 
                tb_bhierarchy, 
                tb_address, 
                tb_boundary, 
                tb_academic_year, 
                tb_programme, 
                tb_assessment, 
                tb_question, 
                tb_class, 
                tb_child, 
                tb_student_class,
                tb_student_eval,
                tb_school_info,
                tb_sys_data,
                tb_sys_questions, 
                tb_sys_images,
                vw_boundary_coord, 
                vw_inst_coord 
TO web;

GRANT UPDATE ON tb_sys_data,tb_sys_images,tb_sys_data_id_seq TO web;
GRANT INSERT ON tb_sys_data,tb_sys_images,tb_sys_qans TO web;
