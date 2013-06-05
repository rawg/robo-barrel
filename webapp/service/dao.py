
import sqlite3
import configuration
import time
import datetime
import os


def connection():
    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config = configuration.read()
    return sqlite3.connect(os.path.join(base_path, config['db']))

conn = connection()

def select(query, values=None, debug=False):
    if debug:
        if values:
            q = query
            for v in values:
                q = q.replace('?', str(v), 1)
            print q
        else:
            print query

    c = conn.cursor()
    result = c.execute(query, values)
    return [row for row in result]

def get_latest(sensor):
    data = select("select unix_epoch, value from reading where sensor_id = ? order by unix_epoch desc limit 1", (sensor, ))
    if (data):
        return {"unix_epoch": data[0][0], "value": data[0][1]}
    else:
        return {"value": None}

def get_recent(sensor, start_date=None, end_date=None):
    if not end_date:
        end_date = int(time.mktime(datetime.datetime.now().timetuple()))
    if not start_date:
        start_date = int(time.mktime((datetime.datetime.now() - datetime.timedelta(minutes=120)).timetuple()))
    
    query = """
        select unix_epoch, value 
        from reading 
        where sensor_id = ?
        and unix_epoch >= ?
        and unix_epoch <= ?
    """
    
    return select(query, (sensor, start_date, end_date))

class Reading():
    def __init__(self):
        self.unix_epoch = int(time.time())
        self.sensor_id = 0
        self.value = 0

        self.session_id = 0
        self.millis = 0
        
        dt = datetime.datetime.now()

        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self.hour = dt.hour
        self.minute = dt.minute

    def save(self):
        c = conn.cursor()

        query = """
            insert into reading (unix_epoch, sensor_id, value, session_id, millis, year, month, day, hour, minute)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        c.execute(query, (self.unix_epoch, self.sensor_id, self.value, self.sesson_id, self.millis, self.year, self.month, self.day, self.hour, self.minute))

        conn.commit()



class RollUp():

    levels = ['year', 'month', 'day', 'hour']
    deltas = [
        datetime.timedelta(days=1460),
        datetime.timedelta(days=365),
        datetime.timedelta(days=30),
        datetime.timedelta(days=7)
    ]

    def __init__(self):
        pass

    def rollup(self, since = None, level = 'year'):
        if level not in self.levels:
            raise Exception("Invalid level")
        if not since:
            since = int(time.time())

        c = conn.cursor()
        
        c.execute("delete from reading_rollup_%(level)s where unix_epoch >= ?" % locals(), (since, ))

        level_idx = self.levels.index(level)
        levels_list = ", ".join(self.levels[0:level_idx + 1])

        # Build an expression to set the epoch
        dt = "datetime(year"
        if level_idx >= self.levels.index('month'):
            dt += " || '-' || substr('00'||month, -2, 2)"
        else:
            dt += " || '-01'"

        if level_idx >= self.levels.index('day'):
            dt += " || '-' || substr('00'||day, -2, 2)"
        else:
            dt += " || '-01'"

        if level_idx >= self.levels.index('hour'):
            dt += " || ' ' || substr('00'||hour, -2, 2) || ':00'"

        dt += ")"

        query = """
            insert into reading_rollup_%(level)s (avg_value, max_value, min_value, sum_value, sensor_id, unix_epoch, %(levels_list)s)
            select avg(value), max(value), min(value), sum(value), sensor_id, strftime('%%s', %(dt)s), %(levels_list)s
            from reading
            where unix_epoch >= ?
            group by sensor_id, %(levels_list)s
        """ % locals()
        
        c.execute(query, (since, ))
        
        conn.commit()

    @staticmethod
    def fetch(level, sensor, start_date=None, end_date=None):

        if level not in RollUp.levels:
            raise Exception("Invalid level")
        
        idx = RollUp.levels.index(level)

        if not end_date:
            end_date = int(time.mktime(datetime.datetime.now().timetuple()))
        if not start_date:
            start_date = int(time.mktime((datetime.date.today() - RollUp.deltas[idx]).timetuple()))

        fields = ", ".join(RollUp.levels[0:idx + 1])
        print fields
        query = """
            select avg_value, max_value, min_value, sum_value, unix_epoch, %(fields)s
            from reading_rollup_%(level)s
            where sensor_id = ?
            and unix_epoch >= ?
            and unix_epoch <= ?
        """ % locals()

        return select(query, (sensor, start_date, end_date), True)

