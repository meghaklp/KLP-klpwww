-- Aggregation tables

DROP TABLE IF EXISTS "tb_school_agg";
CREATE TABLE "tb_school_agg" (
  "id" integer,
  "name" varchar(300),
  "bid" integer,
  "sex" sex,
  "num" integer
);

DROP TABLE IF EXISTS "tb_school_assess_agg";
CREATE TABLE "tb_school_assess_agg" (
  "sid" integer REFERENCES "tb_school" ("id") ON DELETE CASCADE,
  "assid" integer REFERENCES "tb_assessment" ("id") ON DELETE CASCADE,
  "clid" integer REFERENCES "tb_class" ("id") ON DELETE CASCADE,
  "sex" sex,
  "mt" school_moi,
  "aggtext" varchar(100) NOT NULL,
  "aggval" numeric(6,2) DEFAULT 0
);

CREATE OR REPLACE function agg_school(int) returns void as $$
declare
        schs RECORD;
begin
        for schs in SELECT s.id as id, s.name as name, s.bid as bid, c.sex as sex, count(stu.id) AS count
                 FROM tb_student stu, tb_class cl, tb_student_class sc, tb_child c, tb_school s
                 WHERE cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND sc.status=1 AND stu.cid = c.id AND sc.ayid = $1
                 GROUP BY s.id, s.name, s.bid, c.sex 
        loop
                insert into tb_school_agg values (schs.id, schs.name, schs.bid, schs.sex, schs.count);
        end loop;
end;
$$ language plpgsql;

CREATE OR REPLACE function agg_school_grade(int, int) returns void as $$
declare
        stueval RECORD;
begin
        for stueval in SELECT s.id as id, ass.id as assid, sc.clid as clid, c.sex as sex, c.mt as mt, se.grade as grade, cast(count(distinct stu.id) as float) as cnt
                       FROM tb_student stu, tb_class cl, tb_student_class sc, tb_child c, tb_school s, tb_student_eval se, tb_assessment ass
                       WHERE cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id AND stu.id = se.stuid AND se.assid = ass.id AND ass.id = $1 AND sc.ayid = $2 AND se.grade IS NOT NULL
                       GROUP BY s.id, ass.id, sc.clid, c.sex, c.mt, se.grade
        loop
                insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, stueval.grade, stueval.cnt);
        end loop;
end;
$$ language plpgsql;

CREATE OR REPLACE function agg_school_nng(int, int) returns void as $$
declare
        stueval RECORD;
begin

        for stueval in 
        SELECT id, assid,clid,sex,mt,
        count(case when mark < 20 then id else null end) as Rung1, 
        count(case when mark between 20 and 40 then id else null end) as Rung2,
        count(case when mark between 40 and 60 then id else null end) as Rung3,
        count(case when mark between 60 and 80 then id else null end) as Rung4,
        count(case when mark > 80 then id else null end) as Rung5
        FROM ( SELECT se.stuid,s.id as id, ass.id as assid, sc.clid as clid, c.sex as sex, c.mt as mt, avg(se.mark) as mark 
               FROM tb_student stu, tb_class cl, tb_student_class sc, tb_child c, tb_school s, tb_student_eval se, tb_assessment ass 
               WHERE cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id AND stu.id = se.stuid AND se.assid = ass.id AND ass.id = $1 AND sc.ayid =$2  
               GROUP BY s.id, ass.id, sc.clid, c.sex, c.mt,se.stuid ) as output 
        GROUP BY id,assid,clid,sex,mt
        loop
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung1', stueval.Rung1);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung2', stueval.Rung2);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung3', stueval.Rung3);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung4', stueval.Rung4);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung5', stueval.Rung5);
        end loop;

end;
$$ language plpgsql;

CREATE OR REPLACE function agg_school_ang(int, int) returns void as $$
declare
        stueval RECORD;
        domains text[7];
        dqmax integer[7];
        dqmin integer := 1;
begin
        domains[1] = 'General awareness'; dqmax[1] = 5;
        domains[2] = 'Gross motor'; dqmax[2] = 9;
        domains[3] = 'Fine motor'; dqmax[3] = 15;
        domains[4] = 'Language'; dqmax[4] = 28;
        domains[5] = 'Intellectual'; dqmax[5] = 33;
        domains[6] = 'Socio-emotional'; dqmax[6] = 37;
        domains[7] = 'Pre-academic'; dqmax[7] = 56;

        for i in 1..7 loop
            for stueval in SELECT s.id as id, ass.id as assid, sc.clid as clid, c.sex as sex, c.mt as mt, avg(cast(se.grade as integer)) as dmarks
                       FROM tb_student stu, tb_class cl, tb_student_class sc, tb_child c, tb_school s, tb_student_eval se, tb_assessment ass, tb_question q
                       WHERE cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id AND stu.id = se.stuid AND se.assid = ass.id AND ass.id = $1 AND sc.ayid = $2 AND se.qid = q.id AND ass.id = q.assid AND cast(q.desc as integer) between dqmin and dqmax[i]
                       GROUP BY s.id, ass.id, sc.clid, c.sex, c.mt
                       ORDER BY s.id
            loop
                   insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, domains[i], stueval.dmarks);
            end loop;
            dqmin := dqmax[i] + 1;
        end loop;

end;
$$ language plpgsql;

CREATE OR REPLACE function agg_school_eng(int, int) returns void as $$
declare
        stueval RECORD;
begin

        for stueval in 
        SELECT id, assid,clid,sex,mt,
        count(case when mark < 20 then id else null end) as Rung1, 
        count(case when mark between 20 and 40 then id else null end) as Rung2,
        count(case when mark between 40 and 60 then id else null end) as Rung3,
        count(case when mark between 60 and 80 then id else null end) as Rung4,
        count(case when mark > 80 then id else null end) as Rung5
        FROM ( SELECT se.stuid,s.id as id, ass.id as assid, sc.clid as clid, c.sex as sex, c.mt as mt, case when se.qid between 145 and 149 then avg(cast(se.mark as integer) *100) when se.qid between 139 and 145 then avg(se.mark) end as mark
               FROM tb_student stu, tb_class cl, tb_student_class sc, tb_child c, tb_school s, tb_student_eval se, tb_assessment ass 
               WHERE cl.sid = s.id AND sc.clid = cl.id AND sc.stuid = stu.id AND stu.cid = c.id AND stu.id = se.stuid AND se.assid = ass.id AND ass.id = $1 AND sc.ayid =$2  
               GROUP BY s.id, ass.id, sc.clid, c.sex, c.mt,se.qid,se.stuid ) as output 
        GROUP BY id,assid,clid,sex,mt
        loop
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung1', stueval.Rung1);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung2', stueval.Rung2);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung3', stueval.Rung3);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung4', stueval.Rung4);
               insert into tb_school_assess_agg values (stueval.id, stueval.assid, stueval.clid, stueval.sex, stueval.mt, 'Rung5', stueval.Rung5);
        end loop;

end;
$$ language plpgsql;



-- Populate tb_school_agg for the current academic year
select agg_school(101);
-- 2006 Reading
select agg_school_grade(9, 90);
select agg_school_grade(10, 90);
select agg_school_grade(11, 90);
select agg_school_grade(12, 90);
-- 2009 Reading
select agg_school_grade(15, 119);
select agg_school_grade(16, 119);
select agg_school_grade(17, 119);
select agg_school_grade(18, 119);
-- 2009 Target reading
select agg_school_grade(26, 119);
-- 2007 NNG
select agg_school_nng(3, 1);
select agg_school_nng(4, 1);
-- 2008 NNG
select agg_school_nng(5, 2);
select agg_school_nng(6, 2);
-- ಪರಿಹರ ಬೊಧನೆ  (2008 Reading)
select agg_school_grade(13, 2);
select agg_school_grade(14, 2);
-- -- 2009 NNG
select agg_school_nng(7, 119);
select agg_school_nng(8, 119);
-- 2009 Ramanagra NNG1
select agg_school_nng(21, 119);
select agg_school_nng(22, 119);
-- 2009 Ramanagra NNG2
select agg_school_nng(23, 119);
select agg_school_nng(24, 119);
-- 2009 Target NNG
select agg_school_nng(25,119);
-- 2009 Anganwadi
select agg_school_ang(1, 119);
select agg_school_ang(2, 119);
--2009 English
select agg_school_eng(19,119);
select agg_school_eng(20,119);

GRANT SELECT ON tb_school_agg,
                tb_school_assess_agg
TO web;
