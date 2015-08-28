create table users (
  id integer primary key,
  ISUname CHAR(12) not null ,
  nickname NCHAR(13),
  password char(40) not null ,
  email char(40),
  signature nchar(20),
  sex char(1) ,
  phone char(11),
  city NCHAR(20),
  unique(ISUname),
  check (length(phone) == 13)
);