copy tb_bhierarchy from '/home/st/www/klpsite/importers/load/tb_bhierarchy.csv' with csv;
copy tb_boundary from '/home/st/www/klpsite/importers/load/tb_boundary.csv' with csv;
copy tb_address from '/home/st/www/klpsite/importers/load/tb_address.csv' with csv;
copy tb_school from '/home/st/www/klpsite/importers/load/tb_school.csv' with csv;
copy tb_child from '/home/st/www/klpsite/importers/load/tb_child.csv' with csv;
copy tb_class from '/home/st/www/klpsite/importers/load/tb_class.csv' with csv;
copy tb_academic_year from '/home/st/www/klpsite/importers/load/tb_academic_year.csv' with csv;
copy tb_student from '/home/st/www/klpsite/importers/load/tb_student.csv' with csv;
copy tb_student_class from '/home/st/www/klpsite/importers/load/tb_student_class.csv' with csv;
copy tb_question from '/home/st/www/klpsite/importers/load/tb_question.csv' with csv;
copy tb_student_eval from '/home/st/www/klpsite/importers/load/tb_student_eval.csv' with csv;
vacuum analyze;
