from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import glob 
from subprocess import Popen


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

def main():
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()

    state = ''
    district = ''
    block = ''
    icount = 0
    driver.get("http://omms.nic.in/Home/")
    time.sleep(10)
    main_menu = driver.find_element_by_css_selector("a.menuLnk")
    main_click = main_menu.get_attribute('onclick')
    time.sleep(3)
    driver.execute_script("return "+main_click)
    time.sleep(3)

    print "Getting all states, districts and blocks..."
    state_element = driver.find_element_by_xpath("//select[@name='StateCode']")
    state_options = state_element.find_elements_by_tag_name("option")
    state_count = len(state_options)
    for state_i in xrange(1,state_count):
        state_option = get_i_option(driver, "StateCode", state_i)
        state = state_option.text
        state_option.click()

        district_element = driver.find_element_by_xpath("//select[@name='DistrictCode']")
        district_options = district_element.find_elements_by_tag_name("option")
        district_count = len(district_options)
        for district_i in xrange(1,district_count):
            district_option = get_i_option(driver, "DistrictCode", district_i)
            district = district_option.text
            district_option.click()
            block_element = driver.find_element_by_xpath("//select[@name='BlockCode']")
            block_options = block_element.find_elements_by_tag_name("option")
            block_count = len(block_options)
            for block_i in xrange(1,block_count):
                block_option = get_i_option(driver, "BlockCode", block_i)
                block = block_option.text

                icount = 0
                for year in range(2000,2017):
                    #State: Rajasthan     District: Ajmer     Block: Arain     Year : 2000-2001      Batch: All Batches   
                    print "Accessing data for state: ", state, " district: ", district, " block: ", block, " year: ", year,"..."
                    year = str(year)
                    time.sleep(5)
                    access_string =  str("http://omms.nic.in/MvcReportViewer.aspx?_r=%2fPMGSYCitizen%2fSanctionedProjects&Level=3&State=29&District=6&Block=216&Year="+year+"&Batch=0&PMGSY=1&DisplayStateName="+state+"&DisplayDistName="+district+"&DispBlockName="+block+"&LocalizationValue=en&BatchName=All+Batches")
                    time.sleep(5) 
                    driver.get(access_string)
                    #let it load
                    time.sleep(20)

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
                    icount += 1

                    harvest(icount)


    driver.close()
    display.stop()


if __name__=='__main__':
    main()
