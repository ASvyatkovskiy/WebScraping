from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import glob 
from subprocess import Popen


def db_load(driver,state,district,block,year):
    #State: Rajasthan     District: Ajmer     Block: Arain     Year : 2000-2001      Batch: All Batches   
    year = str(year)
    print "Loading data for Rajasthan year ",year
    driver.get("http://omms.nic.in/MvcReportViewer.aspx?_r=%2fPMGSYCitizen%2fSanctionedProjects&Level=3&State=29&District=6&Block=216&Year="+year+"&Batch=0&PMGSY=1&DisplayStateName="+state+"&DisplayDistName="+district+"&DispBlockName="+block+"&LocalizationValue=en&BatchName=All+Batches")
    #let it load
    time.sleep(5)

    #Find the right CSS web element using Chrome
    elem = driver.find_elements_by_css_selector("div[id$='208iT0R0x0'] > a")
    time.sleep(3)
    hov = ActionChains(driver).move_to_element(elem[1])
    hov.perform()
    time.sleep(3)
    elem[1].click()
    time.sleep(5)

    link = driver.find_elements_by_css_selector('div#ReportViewer_ctl05_ctl04_ctl00_Menu > div > a')
    button_name = link[1].get_attribute('onclick')
    time.sleep(3)
    driver.execute_script("return "+button_name)
    #Allow to finish download
    time.sleep(5)

    #change filename: it assumes there is no xlsx prior
    xlsx_file = glob.glob("/tmp/*.xlsx*")
    if len(xlsx_file) > 1: print "Unknown output detected!"
    elif len(xlsx_file) < 1: print "No output produced!" 
    Popen("mv "+xlsx_file[0]+" ./output_"+state+"_"+district+"_"+block+"_"+year+".xlsx",shell=True).wait()


def main():
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()

    years = range(2000,2003) #2017)
    states = [ 'Andhra+Pradesh', 'Arunachal+Pradesh', 'Assam','Bihar', 'Chhattisgarh'] #, 'Goa', 'Gujarat', 'Haryana', 'Himachal+Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']

    #https://github.com/pigshell/india-census-2011/blob/master/pca-total.csv
    districts = ['Ajmer','Ambala']
    blocks = ['Arain']
    for state in states:
        for district in districts:
            for block in blocks:
                map(lambda x: db_load(driver,state,district,block,x),years)

    driver.close()
    display.stop()

if __name__=='__main__':
    main()
