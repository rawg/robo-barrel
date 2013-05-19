

import sqlite3
import configuration
import time

class RollUp():

    levels = ['year', 'month', 'day', 'hour']

    def __init__(self):
        pass

    def rollup(self, since = None, level = 'year'):
        if level not in self.levels:
            raise Exception("Invalid level")
        if not since:
            since = int(time.time())

        config = configuration.read()
        conn = sqlite3.connect(config['db'])
        c = conn.cursor()

        levels_list = ", ".join(self.levels[0:self.levels.index(level) + 1])

        query = """
            insert into reading_rollup_%(level)s
            select avg(reading), sensor, %(levels_list)s
            from reading
            where effective > ?
            group by sensor, %(levels_list)s
        """ % locals()

        print query

if __name__ == '__main__':
    RollUp().rollup()
