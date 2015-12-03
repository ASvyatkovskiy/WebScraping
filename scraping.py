#!/usr/bin/env python

import urllib2
import re
from bs4 import BeautifulSoup
import time

from joblib import Parallel, delayed
import multiprocessing


#
#Get links
#
start = time.time()
nsubpages = 10 #331 folded pages by eye

num_cores = multiprocessing.cpu_count()
print "Running on ", num_cores, " CPU cores"
real_links = list()

def doPage(ipage):
        page = urllib2.urlopen('http://www.mothering.com/forum/306-unassisted-childbirth/index'+str(ipage)+'.html').read()
        soup = BeautifulSoup(page)
        links = soup.findAll(href = re.compile("http://www.mothering.com/forum/306-unassisted-childbirth/\d+(-.*)+.html$"))
        return map(lambda x: x['href'],links)

real_links = Parallel(n_jobs=num_cores)(delayed(doPage)(ipage) for ipage in range(nsubpages))

#somehow we get duplicates.... so set() it
real_links = set([item for sublist in real_links for item in sublist])
end = time.time()
print "Elapsed time %s" % (end-start)

#
#Get texts
#

texts = list()
  
def doTexts(l):
    post = urllib2.urlopen(l).read()
    soup = BeautifulSoup(post)

    tech_divs = soup.find_all('div', attrs={'id': re.compile('post_message_\d*')})
    tech_divs = filter(lambda x: x!= None,tech_divs)
    return map(lambda x: x.get_text().strip(),tech_divs)  

texts = Parallel(n_jobs=num_cores)(delayed(doTexts)(l) for l in real_links)  
#texts = [item for sublist in texts for item in sublist]

end2 = time.time()
print "Total elapsed time %s" % (end2-start)

print len(texts)
#print texts[0]
#You will now have all the comment in texts list
