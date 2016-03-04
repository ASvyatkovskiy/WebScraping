from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import glob 
from subprocess import Popen
import cPickle as pickle

from joblib import Parallel, delayed
import multiprocessing

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_i_option(driver, name, i):
    element = driver.find_element_by_name(name)
    options = element.find_elements_by_tag_name("option")
    return options[i]

def harvest(count):
    #change filename: it assumes there is no xlsx prior
    count = str(count)
    xlsx_file = glob.glob("/tmp/*.xlsx*")
    if len(xlsx_file) > 1: print "Unknown output detected!"
    elif len(xlsx_file) < 1: print "No output produced!" 
    Popen("mv "+xlsx_file[0]+" ./output_"+count+".xlsx",shell=True).wait()

def get_all_items():
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()

    driver.get("http://omms.nic.in/Home/")
    main_menu = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a.menuLnk")))
    #main_menu = driver.find_element_by_css_selector("a.menuLnk")
    main_click = main_menu.get_attribute('onclick')
    time.sleep(3)
    driver.execute_script("return "+main_click)
    time.sleep(3)


    print "Getting all states, districts and blocks..."
    all_items = dict()
    state_element = driver.find_element_by_xpath("//select[@name='StateCode']")
    state_options = state_element.find_elements_by_tag_name("option")
    state_count = len(state_options)
    for state_i in xrange(1,state_count):
        state_option = get_i_option(driver, "StateCode", state_i)
        state = (state_option.get_attribute("value"),state_option.text)
        print "state ", state
        all_items[state] = dict()
        state_option.click()
        time.sleep(3)

        district_element = driver.find_element_by_xpath("//select[@name='DistrictCode']")
        district_options = district_element.find_elements_by_tag_name("option")
        district_count = len(district_options)
        ##case when there is no district 
        district_start = 1
        if district_count == 0:
            district_start = 0
            district_count = 1
        for district_i in xrange(district_start,district_count):
            try: 
                district_option = get_i_option(driver, "DistrictCode", district_i)
                district = (district_option.get_attribute("value"),district_option.text)
            except: district = (0,"All+Districts")
            print "district ", district
            all_items[state][district] = list()
            district_option.click()
            time.sleep(7)  

            block_element = driver.find_element_by_xpath("//select[@name='BlockCode']")
            block_options = block_element.find_elements_by_tag_name("option")
            block_count = len(block_options)
            #case when there is no block
            block_start = 1
            if block_count == 0:
                block_start = 0
                block_count = 1
            for block_i in xrange(block_start,block_count):
                #print "block_i ", block_i
                try:
                    block_option = get_i_option(driver, "BlockCode", block_i)
                    block = (block_option.get_attribute("value"),block_option.text)
                except: block = (0,"All+Blocks")
                print "block ", block
                all_items[state][district].append(block)
    driver.close()
    display.stop()

    return all_items

def process_chunk(state,district,block):
   
    try:
        display = Display(visible=0, size=(1024, 768))
        display.start()
        driver = webdriver.Firefox()

        driver.get("http://omms.nic.in/Home/")
        main_menu = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a.menuLnk")))
        #main_menu = driver.find_element_by_css_selector("a.menuLnk")
        main_click = main_menu.get_attribute('onclick')
        time.sleep(3)
        driver.execute_script("return "+main_click)
        time.sleep(3)

        for year in range(2000,2017):
            #State: Rajasthan     District: Ajmer     Block: Arain     Year : 2000-2001      Batch: All Batches   
            print "Accessing data for state: ", state, " district: ", district, " block: ", block, " year: ", year,"..."
            year = str(year)
            access_string = str("http://omms.nic.in/MvcReportViewer.aspx?_r=%2fPMGSYCitizen%2fSanctionedProjects&Level=3&State="+state[0]+"&District="+district[0]+"&Block="+block[0]+"&Year="+year+"&Batch=0&PMGSY=1&DisplayStateName="+state[1]+"&DisplayDistName="+district[1]+"&DispBlockName="+block[1]+"&LocalizationValue=en&BatchName=All+Batches") 
            time.sleep(5) 
            #print access_string
            driver.get(access_string)
            #let it load
            time.sleep(10)

            #Find the right CSS web element using Chrome
            elem = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div[id$='208iT0R0x0'] > a")))
            time.sleep(3)
            hov = ActionChains(driver).move_to_element(elem[1])
            hov.perform()
            time.sleep(3)
            elem[1].click()
            time.sleep(5)

            link = driver.find_elements_by_css_selector('div#ReportViewer_ctl05_ctl04_ctl00_Menu > div > a')
            button_name = link[1].get_attribute('onclick')
            time.sleep(3)
            try:
                driver.execute_script("return "+button_name)
            except: print "Page is being updated"
            #Allow to finish download
            time.sleep(5)

            #harvest(state,district,block,year)

        driver.close()
        display.stop()
    except: 
        print "Unknown exception" 
        pass

def main():

    try:
        all_items = pickle.load( open( "all_items.pickle", "rb" ) )
    except:
        all_items = get_all_items()
        pickle.dump(all_items, open( "all_items.pickle", "wb" ) )

    num_cores = 1
    for state in all_items.keys():
        #insert or uncomment something like this to restrict to 1 state
        #if state[1] != 'Rajasthan': continue
        for district in all_items[state].keys():
            Parallel(n_jobs=num_cores)(delayed(process_chunk)(state,district,block) for block in all_items[state][district])

if __name__=='__main__':
    main()
    print "Now run the output parser script to collect the output files."
