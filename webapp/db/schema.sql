

create table if not exists sensor (
	id int primary key,
	title text
);

create table if not exists reading (
	unix_epoch integer, -- date unix_epoch
	sensor_id integer, -- FK: sensor.id
	value real,
	
	session_id integer, -- Arduino session ID
	millis integer, -- Time of reading in Arduino session

	year integer,
	month integer,
	day integer,
	hour integer,
	minute integer,

	foreign key (sensor_id) references sensor (id)

);

-- only the latest readings
create table if not exists latest_reading (
	sensor_id integer,
	value real,

	foreign key (sensor_id) references sensor (id)
);

-- roll ups
create table if not exists reading_rollup_hour (
	sensor_id integer,
	avg_value real,
	max_value real,
	min_value real,
	sum_value real,
	year integer,
	month integer,
	day integer,
	hour integer,
	unix_epoch integer,
	foreign key (sensor_id) references sensor (id)
);

create table if not exists reading_rollup_day (
	sensor_id integer,
	avg_value real,
	max_value real,
	min_value real,
	sum_value real,
	year integer,
	month integer,
	day integer,
	unix_epoch integer,
	foreign key (sensor_id) references sensor (id)
);

create table if not exists reading_rollup_month (
	sensor_id integer,
	avg_value real,
	max_value real,
	min_value real,
	sum_value real,
	year integer,
	month integer,
	unix_epoch integer,
	foreign key (sensor_id) references sensor (id)
);


