-- tables for tests only. The indises removed. --
create table kladr_socr
(
	socr  varchar(10) not null,			-- SCNAME
	name  varchar(29) not null,			-- SOCRNAME
	level varchar(5)  not null,			-- LEVEL
	tcode varchar(3)  not null			-- KOD_T_ST
);

create table kladr_kladr
(
	code  varchar(13) not null primary key,	-- CODE [0:11] SS RRR GGG PPP AA
	level int not null,                     -- [1 .. 4]  
	name  varchar(40) not null,			    -- NAME
	socr  varchar(10) not null,			    -- SOCR
	stat  varchar(1)  not null,			    -- STATUS
	indx  varchar(6)  not null		        -- INDEX (postal index)
);

create table kladr_street
(
	code  varchar(17) not null primary key,	-- CODE [0:15] SS RRR GGG PPP UUUU AA
	-- level always should be 5
	name  varchar(40) not null,			    -- NAME
	socr  varchar(10) not null,			    -- SOCR
	indx  varchar(6)  not null		        -- INDEX (postal index)
);

create table kladr_doma
(
	code  varchar(19) not null primary key,	-- CODE [0:19] SS RRR GGG PPP UUUU DDDD
	-- level always should be 6
	name  varchar(40) not null,			    -- NAME
	korp  varchar(10) not null,			    -- KORP
	indx  varchar(6)  not null		        -- INDEX (postal index)
);
