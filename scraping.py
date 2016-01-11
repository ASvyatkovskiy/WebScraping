#!/usr/bin/env python

import urllib2
import mechanize
import cookielib
import re
from bs4 import BeautifulSoup
import time
from joblib import Parallel, delayed
import multiprocessing
import sys
import csv

def doPage(main_url,ipage):
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.addheaders = [('User-agent', 'Chrome')]

    # The site we will navigate into, handling it's session
    br.open('http://www.mothering.com/forum/login.php?do=login')

    # View available forms
    #for f in br.forms():
    #    print f

    # Select the second (index one) form (the first form is a search query box)
    br.select_form(nr=1)

    # User credentials
    br.form['vb_login_username'] = 'yourusername'
    br.form['vb_login_password'] = 'yourpasswd'
    # Login
    br.submit()

    page = br.open(main_url+'/index'+str(ipage)+'.html').read()
    soup = BeautifulSoup(page)
    links = soup.findAll(href = re.compile(main_url+"/\d+(-.*)+.html$"))
    return map(lambda x: x['href'],links)

#
#Get texts, usernames and timestamps
#
def doTexts(l):
    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    br.addheaders = [('User-agent', 'Chrome')]

    # The site we will navigate into, handling it's session
    br.open('http://www.mothering.com/forum/login.php?do=login')

    # View available forms
    #for f in br.forms():
    #    print f

    # Select the second (index one) form (the first form is a search query box)
    br.select_form(nr=1)

    # User credentials
    br.form['vb_login_username'] = 'yourusername'
    br.form['vb_login_password'] = 'yourpasswd'
    # Login
    br.submit()

    post_lines = list()
    post = ""
    try:
        post_lines = br.open(l).readlines()
        post = br.open(l).read()
    except: print "HTTP 404 probably...", l

    soup = BeautifulSoup(post)
    tech_divs1 = soup.find_all('div', attrs={'id': re.compile('post_message_\d*')})
    tech_divs1 = filter(lambda x: x!= None,tech_divs1)
    texts = map(lambda x: x.get_text().strip().encode("utf-8").translate(None,'\t\r\n'),tech_divs1)

    dates = re.findall("dateCreated\">\d+-\d+-\d+, \d+:\d+ A?P?M", post)
    dates2 = map(lambda x: x.lstrip("dateCreated\">"), dates)

    usernames = filter(lambda x: "nofollow\" class=\"bigusername" in x,post_lines)
    usernames2 = map(lambda x: x.split(">")[-2], usernames)
    usernames3 = map(lambda x: x.rstrip("</a"), usernames2)

    if len(texts) == len(dates2):
        return zip(usernames3,dates2,texts)
    else: return [("","","")]

def main():

    #configurable parameters
    num_cores = 30 #multiprocessing.cpu_count()
    main_urls = [("http://www.mothering.com/forum/306-unassisted-childbirth",331),
      #("http://www.mothering.com/forum/69-vaccinations-archives",1),
      ("http://www.mothering.com/forum/443-i-m-not-vaccinating",191),
      ("http://www.mothering.com/forum/373-selective-delayed-vaccination",114),
      ("http://www.mothering.com/forum/17507-vaccinating-schedule",7)
      ]
    for main_url,nsubpages in main_urls:
        forum_label = main_url.split("/")[-1]

        start = time.time()
        print "Running on ", num_cores, " CPU cores"
        print "Scraping ",forum_label
        real_links = Parallel(n_jobs=num_cores)(delayed(doPage)(main_url,ipage) for ipage in range(nsubpages))
        #somehow we get duplicates.... so set() it
        real_links = set([item for sublist in real_links for item in sublist])
        end = time.time()
        print "Elapsed time %s" % (end-start)
        #print real_links

        results = Parallel(n_jobs=num_cores)(delayed(doTexts)(l) for l in real_links)
        results = [item for sublist in results for item in sublist]

        #save the data
        with open(forum_label+'_out.csv','w') as out:
            csv_out=csv.writer(out,delimiter='|')
            csv_out.writerow(['username','timestamp','text'])
            for row in results:
                csv_out.writerow(row)

        end2 = time.time()
        print "Total elapsed time %s" % (end2-start)

        #Validate
        #for l in results:
        #   print l,"\n"

if __name__=='__main__':
    main()
