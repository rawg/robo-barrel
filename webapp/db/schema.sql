

create table if not exists sensor (
	id int primary key,
	desc text
);

create table if not exists reading (
	effective integer, -- date effective
	sensor integer, -- FK: sensor.id
	reading real,

	year integer,
	month integer,
	day integer,

	foreign key (sensor) references sensor (id)

);

create table if not exists latest_reading (
	sensor integer,
	reading real,

	foreign key (sensor) references sensor (id)
);
