-- Stuff that needs to be worked around from the Oracle data
-- Created: Wed, 16 Jun 2010 20:42:51 IST
-- (C) Alok G Singh <alok@klp.org.in>

-- This code is released under the terms of the GNU GPL v3 
-- and is free software

-- Fix spelling
update tb_boundary set name = 'bangalore' where id = 8877;
