create table user_profiles (
  ISUname char(12) references users(ISUname)
  on delete cascade,
  photo blob
);