

import dao
import sys
import re
import datetime
import time

if __name__ == '__main__':

    #RollUp().rollup()
    terms = []
    for term in sys.argv[1:]:
        terms += re.split('[\-\:\/]', term)

    ints = []
    for term in terms:
        ints.append(int(term))

    idx = len(ints) - 1
    if idx >= len(dao.RollUp.levels):
        idx = len(dao.RollUp.levels) - 1

    level = dao.RollUp.levels[idx]
    ints += [1, 1, 1, 1]
    terms = ints[:4]
    
    unix_epoch = int(time.mktime(datetime.datetime(terms[0], terms[1], terms[2], terms[3]).timetuple()))

    print(unix_epoch, terms, level)
    dao.RollUp().rollup(since=unix_epoch, level=level)


