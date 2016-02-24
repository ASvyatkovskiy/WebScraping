from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import glob 
from subprocess import Popen

def main():
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()

    def db_load(year):
        year = str(year)
        print "Loading data for Rajasthan year ",year
        driver.get("http://omms.nic.in/MvcReportViewer.aspx?_r=%2fPMGSYCitizen%2fSanctionedProjects&Level=3&State=29&District=6&Block=216&Year="+year+"&Batch=0&PMGSY=1&DisplayStateName=Rajasthan&DisplayDistName=Ajmer&DispBlockName=Arain&LocalizationValue=en&BatchName=All+Batches")
        #let it load
        time.sleep(10)

        #Find the right CSS web element using Chrome
        elem = driver.find_elements_by_css_selector("div[id$='208iT0R0x0'] > a")
        time.sleep(5)
        hov = ActionChains(driver).move_to_element(elem[1])
        hov.perform()
        time.sleep(5)
        elem[1].click()
        time.sleep(10)

        link = driver.find_elements_by_css_selector('div#ReportViewer_ctl05_ctl04_ctl00_Menu > div > a')
        button_name = link[1].get_attribute('onclick')
        time.sleep(5)
        driver.execute_script("return "+button_name)
        #Allow to finish download
        time.sleep(10)
        return 0 

    years = range(2000,2017)
    map(lambda x: db_load(x),years)

    driver.close()
    display.stop()

    #harvest all xlsx files in the /tmp folder
    xlsx_files = glob.glob("/tmp/*.xlsx*")
    def harvest(fname):
        Popen("mv "+fname+" ./"+fname.lstrip("/tmp/").rstrip(".part"),shell=True).wait()
    map(lambda x: harvest(x),xlsx_files)

if __name__=='__main__':
    main()
