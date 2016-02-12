from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
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
        driver.get("http://omms.nic.in/MvcReportViewer.aspx?_r=%2fPMGSYCitizen%2fUspCrPropPendingList&Level=1&State=29&District=0&Block=0&Year="+year+"&Batch=0&Collaboration=0&PMGSY=1&LocationName=Rajasthan&DistrictName=All+Districts&BlockName=All+Blocks&LocalizationValue=en&BatchName=All+Batches&CollaborationName=All+Collaborations")

        #Find the right CSS web element using Chrome
        elem = driver.find_elements_by_css_selector('div#ReportViewer_ctl05_ctl04_ctl00_Menu > div > a')
        button_name = elem[1].get_attribute('onclick')
        time.sleep(10)
        driver.execute_script("return "+button_name)
        #Allow to finish download
        time.sleep(30)

    years = [y for y in range(2000,2016)]
    print years
    map(lambda x: db_load(x),years)

    driver.close()
    display.stop()

    #harvest all xlsx files in the /tmp folder
    xlsx_files = glob.glob("/tmp/*.xlsx*")
    def harvest(fname):
        Popen("mv /tmp/"+fname+" ./"+fname.lstrip(".part"),shell=True).wait()
    map(lambda x: harvest(x),xlsx_files)

if __name__=='__main__':
    main()
