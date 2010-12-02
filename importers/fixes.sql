-- Stuff that needs to be worked around from the Oracle data
-- Created: Wed, 16 Jun 2010 20:42:51 IST
-- (C) Alok G Singh <alok@klp.org.in>

-- This code is released under the terms of the GNU GPL v3 
-- and is free software

-- Fix spelling
update tb_boundary set name = 'bangalore' where id = 8877;

-- Add question for reading 2009 (as it shared the question with reading 2008)
insert into tb_question values('40','15','Reading');

--Change 20th day for Reading 2009 to Mid test
update tb_assessment set name='Mid test' where id=18;
