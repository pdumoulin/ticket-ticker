
import sys
import pickle

from pprint import pformat

command = sys.argv[1]
pickles = sys.argv[2]

if command == 'delete':
    pickle.dump({}, open(pickles, 'wb'))
elif command == 'get':
    print pformat(pickle.load(open(pickles, 'rb')))
else:
    print "Unrecognized command '%s'!" % command

