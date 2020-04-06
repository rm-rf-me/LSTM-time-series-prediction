import numpy
import pandas as pd
import time
import datetime
import json
from matplotlib.pylab import plt


configs = json.load(open('../config.json', 'r'))
data = pd.read_csv('../data/a_data.csv')

id = data['id'][0]
count = 0
maxx = 0
minn = 10000
tot = 0
mean = 0.0

ids = []
counts = []
maxxs = []
minns = []
means = []

fig = plt.figure (facecolor='white')
ax1 = plt.subplot(1,1,1,facecolor='white')

for col in range(data.shape[0]) :
    if(id == data['id'][col]) :
        count += 1
        maxx = max (maxx, data['ele'][col])
        minn = min (minn, data['ele'][col])
        tot += data['ele'][col]
    else :
        mean = (1.0 * tot) / count
        ids.append(id)
        counts.append(count)
        maxxs.append(maxx)
        minns.append(minn)
        means.append(mean)
        print ("id:", id, " count:", count, " maxx:", maxx, " minn:", minn, " mean:", mean)
        id = data['id'][col]
        count = 0
        tot = 0
        maxx = 0
        minn = 10000
print ("id:", id, " count:", count, " maxx:", maxx, " minn:", minn, " mean:", mean)

#ax1.hist (ids, counts, histtype='bar', facecolor='black')
#plt.bar (ids, counts, color='b')
ax1.plot (ids, means, color='black', label='means')
ax1.plot (ids, maxxs, color='red', label='maxx')
ax1.plot (ids, minns, color='blue', label='minn')
plt.legend ()
plt.show ()