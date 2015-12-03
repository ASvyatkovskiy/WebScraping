#!/usr/bin/env python

import urllib2
import re
from bs4 import BeautifulSoup
import sys

from pyspark import SparkContext
from pyspark.storagelevel import StorageLevel

def doPage(ipage):
        page = urllib2.urlopen('http://www.mothering.com/forum/306-unassisted-childbirth/index'+str(ipage)+'.html').read()
        soup = BeautifulSoup(page)
        links = soup.findAll(href = re.compile("http://www.mothering.com/forum/306-unassisted-childbirth/\d+(-.*)+.html$"))
        return map(lambda x: x['href'],links)

def doTexts(l):
    post = urllib2.urlopen(l).read()
    soup = BeautifulSoup(post)

    tech_divs = soup.find_all('div', attrs={'id': re.compile('post_message_\d*')})
    tech_divs = filter(lambda x: x!= None,tech_divs)
    return map(lambda x: x.get_text().strip(),tech_divs)  

def main(argv):
    sc = SparkContext(appName="WebScraper")
    #
    #Get links
    #
    nsubpages = 331 #folded pages by eye
    subranges_rdd = sc.parallelize([x for x in range(nsubpages)],15)
    real_links_rdd = subranges_rdd.map(lambda x: doPage(x)).flatMap(lambda x: x).distinct().cache()
    #somehow we get duplicates.... so we use distinct()

    #
    #Get texts
    #
    #You will now have all the comment in texts list
    texts_rdd = real_links_rdd.map(lambda x: doTexts(x))
    print len(texts_rdd.collect())
    texts_rdd.saveAsTextFile("/user/alexeys/scraping_out")

if __name__=='__main__':
    main(sys.argv)
