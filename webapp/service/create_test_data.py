
import configuration
import sqlite3
import time
import datetime
import random

def tod_factor(hr):
    return 12 - abs(12 - hr)

def light_level(hr):
    target = 1000 * (12 - abs(hr - 12)) ** 3
    return random.randint(target - 100, target + 100)

def bed_temp(hr):
    return 60 + tod_factor(hr) + random.randint(0, 5)

def humidity(hr):
    return 70 + int(tod_factor(hr) / 2) + random.randint(0, 2)

def moisture(hr):
    moisture.last += random.randint(-10, 10)
    if moisture.last < 850:
        moisture.last = 850
    elif moisture.last > 1100:
        moisture.last = 1100
    
    return moisture.last

moisture.last = 950

def water_level(hr):
    return 1 if random.randint(1, 10) > 1 else 0

sensors = [
    (1, 'Panel Light Level', light_level), 
    (2, 'Bed Light Level', light_level),
    (3, 'Humidity', humidity),
    (4, 'Bed Temperature', bed_temp), 
    (5, 'Moisture', moisture),
    (6, 'Water Level', water_level),
    (7, 'Pump running', water_level)
]

reading_time = time.mktime(datetime.date(2012, 10, 1).timetuple())
sentry_time = time.time()



config = configuration.read()
conn = sqlite3.connect(config['base_path'] + "/" + config['db'])
c = conn.cursor()

#for sensor in sensors:
#    c.execute("insert into sensor (id, title) values (?, ?)", (sensor[0], sensor[1]))

while reading_time < sentry_time:
    for sensor in sensors:
        tm = time.localtime(reading_time)
        reading = sensor[2](tm.tm_hour)
        print sensor[1], reading, tm.tm_hour
        c.execute("insert into reading (sensor_id, value, unix_epoch, year, month, day, hour, minute) values (?, ?, ?, ?, ?, ?, ?, ?)", (sensor[0], reading, reading_time, tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min))
    
    try:
        conn.commit()
    except sqlite3.OperationalError:
        print "IO Error"
        c = conn.cursor()
        # yeah, whatever, it's just test data

    time.sleep(0.005)
    reading_time += 300



