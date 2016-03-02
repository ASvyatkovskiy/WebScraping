#!/usr/bin/env python

import glob
from subprocess import Popen

file_list = glob.glob("/tmp/*xlsx*")
ifile = 1
for f in file_list:
    Popen("mv "+f+" "+str(ifile)+".xlsx",shell=True)
    ifile += 1 
