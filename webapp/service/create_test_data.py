
import configuration
import sqlite3
import time
import datetime
import random

def light_level(hr):
    target = 1000 * (12 - abs(hr - 12)) ** 3
    return random.randint(target - 100, target + 100)

def bed_temp(hr):
    target = (12 - abs(hr - 12)) ** 3 / 60
    return random.randint(65, 65 + target)

def water_level(hr):
    return 1 if random.randint(1, 10) > 1 else 0

sensors = [(1, 'Bed Light Level', light_level), (2, 'Bed Temperature', bed_temp), (3, 'Water Level', water_level)]
reading_time = time.mktime(datetime.date(2012, 10, 1).timetuple())
sentry_time = time.time()



config = configuration.read()
conn = sqlite3.connect(config['base_path'] + "/" + config['db'])
c = conn.cursor()

for sensor in sensors:
    c.execute("insert into sensor (id, title) values (?, ?)", (sensor[0], sensor[1]))

while reading_time < sentry_time:
    for sensor in sensors:
        tm = time.localtime(reading_time)
        reading = sensor[2](tm.tm_hour)
        c.execute("insert into reading (sensor_id, value, unix_epoch, year, month, day, hour, minute) values (?, ?, ?, ?, ?, ?, ?, ?)", (sensor[0], reading, reading_time, tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min))
    
    conn.commit()
    reading_time += 300



