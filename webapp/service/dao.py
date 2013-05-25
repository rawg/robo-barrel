
import sqlite3
import configuration
import time
import os


def connection():
    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config = configuration.read()
    return sqlite3.connect(os.path.join(base_path, config['db']))

class RollUp():

    levels = ['year', 'month', 'day', 'hour']

    def __init__(self):
        pass

    def rollup(self, since = None, level = 'year'):
        if level not in self.levels:
            raise Exception("Invalid level")
        if not since:
            since = int(time.time())

        conn = connection()
        c = conn.cursor()
        
        c.execute("delete from reading_rollup_%(level)s where unix_epoch >= ?" % locals(), (since, ))

        level_idx = self.levels.index(level)
        levels_list = ", ".join(self.levels[0:level_idx + 1])

        # Build an expression to set the epoch
        dt = "datetime(year"
        if level_idx >= self.levels.index('month'):
            dt += " || '-' || month"
        else:
            dt += " || '-01'"

        if level_idx >= self.levels.index('day'):
            dt += " || '-' || day"
        else:
            dt += " || '-01'"

        if level_idx >= self.levels.index('hour'):
            dt += " || ' ' || hour || ':00'"

        dt += ")"

        query = """
            insert into reading_rollup_%(level)s (value, sensor_id, unix_epoch, %(levels_list)s)
            select avg(value), sensor_id, strftime('%%s', %(dt)s), %(levels_list)s
            from reading
            where unix_epoch >= ?
            group by sensor_id, %(levels_list)s
        """ % locals()
        print "querying"
        c.execute(query, (since, ))
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    RollUp().rollup(level='day')
