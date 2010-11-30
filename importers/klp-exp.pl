#!/usr/bin/perl

# Export data from repl_aksems to CSV files that can be imported into the
# klpwww schema that drives the website
# Created: Mon, 07 Jun 2010 17:02:59 IST
# (C) Alok G Singh <alok@klp.org.in>

# This code is released under the terms of the GNU GPL v3 
# and is free software


use strict;
use warnings;

use Cwd;
use Text::CSV;

use Utility::KLPDB qw(connect);

sub make_csv {
    my ($sth, $fname) = @_;

    my $csv = Text::CSV->new({ always_quote => 1,
                               blank_is_undef => 1,
                               auto_diag => 1,
                               eol => "\n" });
    $csv->column_names(@{$sth->{NAME_lc}});
    open my $fh, ">:encoding(utf8)", $fname or die "$fname: $!";
    while (my $row = $sth->fetchrow_arrayref) {
        $csv->print($fh, $row);
    }
    close $fh or die "$fname: $!";
}

my %q_map = (
  133, 7, #2009 NNG
  134, 7,
  135, 7,
  136, 7,

  125,21, #Ramanagara NNG1
  126,21,
  127,21,
  128,21,

  129,23, #Ramanagara NNG2
  130,23,
  131,23,
  132,23
);


my %ignore_qmap = (
    18, 5,
    19, 6
);


# The domain of the map is from the seed data in the schema
# creation script for tb_assessment
my %exam_map = (
    22, 9,                  # 2006 Reading
    23, 10,
    24, 11,
    25, 12,

    28, 3,                  # 2007 NNG
    29, 4,

    26, 5,                  # 2008 NNG
    18, 5,
    27, 6,
    19, 6,

    #15,13,                  #2008 Reading (11 districts)
    #16,14,

    33, 7,                  # 2009 NNG
    36, 8,

    34, 19,                 # English
    40, 20,

    30, 1,                  # 2009 Anganwadi
    37, 2,

    38, 25,                 # Target NNG
    39, 26,                 # Target Reading

    44, 22,                 # 2009 NNG1 Ramanagara
    45, 24,                 # 2009 NNG2 Ramanagara

    #15, 15,                 # 2009 Reading
    #16, 16,
    43, 17,
    35, 18
);

sub make_assess_csv {
    my ($sth, $fname, $col) = @_;
    
    my $csv = Text::CSV->new({ always_quote => 1,
                               blank_is_undef => 1,
                               auto_diag => 1,
                               eol => "\n" });
    $csv->column_names(@{$sth->{NAME_lc}});
    open my $fh, ">:encoding(utf8)", $fname or die "$fname: $!";
    while (my $row = $sth->fetchrow_arrayref) {
        next unless(exists $exam_map{$row->[$col]});
        if ( index($fname,"question") != -1 )#only questions to be ignored
        {
          print STDERR "Question query $row->[$col]";
          if( exists $ignore_qmap{$row->[$col]} ) 
          {
            print STDERR "skipping";
            next;
          }
        }
        if ( exists $q_map{$row->[0]} )
        {
          $row->[$col]=$q_map{$row->[0]};
        }
        else
        { 
          $row->[$col] = $exam_map{$row->[$col]};
        }
        $csv->print($fh, $row);
    }
    close $fh or die "$fname: $!";
}

# Start here
my $klpdb = connect();

# All the one-to-one tables are done via this array.
# The filename is the tablename in klpwww for the sake of the loader script.
# Order is important else COPY will complain about FK errors and die.
# Order of the select clauses should match the order in the schema definition 
# script.

my @queries = (
# tb_bhierarchy
{fname => 'tb_bhierarchy',
 query => q{
select bt.id_bndry_type as id,
       bt.id_heirarchy_type as type,
       bt.parent as parent,
       lower(trim(bt.name)) as name
from   eg_boundary_type bt}},
# tb_boundary
{fname => 'tb_boundary',
 query => q{
select b.id_bndry as id,
       b.parent as parent,
       lower(trim(b.name)) as name,
       bt.id_bndry_type as hid
from   eg_boundary b,
       eg_boundary_type bt
where
       b.id_bndry_type = bt.id_bndry_type
}},
# tb_address
{fname => 'tb_address',
 query => q{
select addressid as id,
       lower(trim(streetaddress1)) as address,
       lower(trim(streetaddress2)) as landmark,
       trim(pincode) as pin
from egclts_address
}},
# tb_school
{fname => 'tb_school',
 query => q{
select s.id as id,
     s.id_adm_boundary as bid,
     s.addressid as aid,
     trim(s.schoolcode) as dise_code,
     trim(s.schoolname) as name,
     trim(sc.category_desc) as cat,
     null as sex,
     lower(trim(i.medium_name)) as moi,
     null as mgmt
from eg_school s,
     eg_school_category sc,
     eg_instr_medium i
where
     s.id_instr_medium = i.id_instr_medium (+)
     and s.categoryid = sc.categoryid (+)
     and s.is_active = 1
}},
# tb_child
{fname => 'tb_child',
 query => q{
select c.childid as id, 
       lower(trim(c.childfname) || ' ' || trim(c.childmname) || ' ' || trim(c.childlname)) as name,
       --to_char(c.dob, 'YYYY-MM-DD') as dob,
       null as dob,
       case when c.gender = 'Boy' then 'male' else 'female' end as sex,
       lower(l.language) as mt
from
       egclts_child c,
       eg_language l
where
       c.languageid = l.languageid (+)
}},
# tb_class
{fname => 'tb_class',
 query => q{
select sg.studentgroupid as id,
       sg.schoolid as sid,
       trim(sg.studgroupname) as class,
       upper(replace(sec.section, 'NoSection')) as section
from egems_studentgroup sg,
     eg_section sec
where
     sg.sectionid = sec.sectionid
     and sg.groupid = 1
}},
# tb_academic_year
{fname => 'tb_academic_year',
 query => q{
select id,
       trim(academicyear) as name
from eg_acadyear_mstr
}},
# tb_student
{fname => 'tb_student',
 query => q{
select stu.studentid as id,
       stu.studentgroupid as clid,
       stu.childid as cid
from egems_student stu
}},
# tb_student_class
{fname => 'tb_student_class',
 query => q{
select scg.studentid as stuid,
       scg.studentgroupid as clid,
       scg.academicyearid as aid,
       stu.statusid as status
from egems_studentgroup sg,
     egems_schstu_association scg,
     egems_student stu
where
     sg.groupid = 1
     and sg.studentgroupid = scg.studentgroupid
     and scg.studentid = stu.studentid
}},
);
my $loadfile = 'load/load.sql';
open my $lf, ">:encoding(utf8)", $loadfile or die "$loadfile: $!";

foreach my $q (@queries) {
    print STDERR "Exporting data for ", $q->{fname}, "\n";
    my $sth = $klpdb->prepare($q->{query});
    $sth->execute();
    # File is created in the load/ subdir
    my $fname = 'load/' . $q->{fname} . '.csv';
    make_csv($sth, $fname);
    printf $lf "copy %s from '%s/%s' with csv;\n", $q->{fname}, cwd(), $fname;
}

# These are queries that need some translation. ce.examid is the one that gets 
# translated according to %exam_map
my @tqueries = (
# tb_question
    {fname => 'tb_question',
     query => q{
select distinct sub.subjectid as id,
       ce.examid as assid,
       sub.subjectname as descrip
from
       eg_subject sub,
       eg_subject_exam se,
       eg_class_exam ce
where
       ce.classexamid = se.classexamid
       and se.subjectid = sub.subjectid
}},
# tb_student_eval
    {fname => 'tb_student_eval',
     query => q{
select sub.subjectid as qid,
       ce.examid as assid,
       cse.studentid as stuid,
       case when se.maxmarks > 0 then cse.marksobtained/se.maxmarks*100 end as mark,
       cse.gradeobtained as grade
from 
       eg_subject sub,
       eg_subject_exam se,
       eg_class_exam ce,
       egems_student stu,
       eg_class_student_eval cse
where
       ce.classexamid = se.classexamid
       and se.subjectid = sub.subjectid
       and se.subjectexamid = cse.subjectexamid
       and cse.studentid = stu.studentid
}},
);

foreach my $q (@tqueries) {
    print STDERR "Exporting data for ", $q->{fname}, "\n";
    my $sth = $klpdb->prepare($q->{query});
    $sth->execute();
    # File is created in the load/ subdir
    my $fname = 'load/' . $q->{fname} . '.csv';
    make_assess_csv($sth, $fname, 1);
    printf $lf "copy %s from '%s/%s' with csv;\n", $q->{fname}, cwd(), $fname;
}
print $lf "vacuum analyze;\n";
close $lf or die "$loadfile: $!";
