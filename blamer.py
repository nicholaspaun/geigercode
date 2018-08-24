import sys, subprocess, os
from collections import Counter

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return int(sum(data)/float(n)) # in Python 2 use sum(data)/float(n)

def median(lst):
    n = len(lst)
    if n < 1:
            return None
    
    return sorted(lst)[n/2]


def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        return 0
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5


def collect():
    os.chdir(sys.argv[1])
    records = {}

    for root, dirs, files in os.walk('.'):
        for f in files:
            realpath = "%s/%s" % (root, f)
            print f
            records[realpath] = Counter()

            blame = subprocess.check_output(['git','blame','-wMC','--line-porcelain',realpath])

            ln = 0
            realHash = None
            for l in blame.split("\n"): 
                try:
                    maybeHash = l[0:40]
                    int(maybeHash,16)
                    realHash = maybeHash                
                except:
                    pass # Maybe wasn't

                lc = l.split(" ")
                if len(lc) != 2:
                    continue # Something else
                
                print lc
                if lc[0] == "committer-time":
                    records[realpath][(realHash,lc[1])] += 1


    return records

def interpret(records):
    for fn, dat in records.iteritems():
        # Drop out insignificant values (changes
        datSig = { k:v for k, v in dat.iteritems() if v > 5}
        if not datSig:
            continue
 
        # Transform to get index by dates
        byDate = dict((int(y), x) for x, y in datSig)
        dates = byDate.keys()

        oldest,avg,stdev,newest,med = min(dates), mean(dates), stddev(dates), max(dates), median(dates)

        struct = {
            'oldest': (byDate[oldest], oldest),
            'newest': (byDate[newest], newest),
            'avg': (avg, stdev),
            'median': (byDate[med], med)
        }
        print struct       

r = collect()
interpret(r)

