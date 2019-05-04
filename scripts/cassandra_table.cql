CREATE KEYSPACE IF NOT EXISTS logs_keyspace WITH replication = {
'class': 'SimpleStrategy', 'replication_factor': 2
};

USE logs_keyspace;

CREATE TABLE logs (
  ip_address text,
  client_identd text,
  user_id text,
  date_time timestamp,
  method text,
  endpoint text,
  protocol text,
  response_code int,
  content_size bigint,
  PRIMARY KEY ((ip_address, content_size, method, endpoint, response_code), date_time)
);
