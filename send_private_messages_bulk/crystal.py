from selenium import webdriver
from selenium.common import exceptions
import time
import json
from itertools import chain
import csv
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import argparse
import logging



# SEARCH_URL = "https://www.linkedin.com/vsearch/p?openFacets=N,G,CC&orig=FCTD&f_N=F"
DIALOG_URL = 'https://www.linkedin.com/'

EMAIL = "......"
PASSWORD = "......."

def get_driver():

    driver = webdriver.Chrome("C:\Users\edward\Documents\my new job\script\chromedriver.exe")  # Optional argument, if not specified will search path.
    #driver.get('http://www.google.com/xhtml');

    driver.get('https://www.linkedin.com')
    print "created driver"
    driver.find_element_by_id('login-email').send_keys(EMAIL)
    driver.find_element_by_id('login-password').send_keys(PASSWORD)
    driver.find_element_by_id('login-password').send_keys('\n')
    time.sleep(60)
	# while 1 min sleep, do manually:
	# open in new tab www.crystalknows.com
	# login and install chrome plugin:  edward.samokhvalov@gmail.com / 1qaz2wsx
    return driver



def process_dialog(fname):
    with open('check_{}.csv'.format(datetime.utcnow()), 'w') as f:
        csv_writer = csv.writer(f)
        input_f = open(fname)
        driver = get_driver()
        driver.get(DIALOG_URL)
        for name in input_f:
            try:
                name = name.strip()
                name = name.decode('utf8')
                i = get_dialog_status(driver, name)
                print i[0], i[1], i[2]
                i = [x.encode('utf8') if type(x) is unicode else x for x in i]
                csv_writer.writerow(i)
                time.sleep(1)
            except Exception as e:
                logging.exception('exc')
                print 'failed', e.message
                driver.get(DIALOG_URL)


def send_msg(driver, name, text):
    driver.find_element_by_id('main-search-box').click()
    name_input = driver.find_element_by_xpath('//input[@id="main-search-box"]')
    name_input.click()
    name_input.clear()
	
	
    #text_input.clear()
    #text = text.split('\n')
    for tx in name:
        name_input.send_keys(tx)
        #time.sleep(0.1)
        #print tx
        #name_input.send_keys(Keys.SHIFT, Keys.ENTER)
    time.sleep(3)
    name_input.send_keys(Keys.ARROW_DOWN)
    time.sleep(3)
    name_input.send_keys(Keys.ENTER)
    time.sleep(6)
	
	#check if this is a profile page (special tag)
    #name_input = driver.find_element_by_name('title')
	#//*[@id="top-card"]/div[2]/div/div[3]/div/div[1]/span/div/div/div[2]/div/div[2]/div/div/div[2]
    try:
	    crystal = driver.find_element_by_xpath('//div[@class="crystal-person-overview"]//div[@class="disc-type"]')
	    #tit = driver.find_element_by_xpath('//div[@id="headline"]/p[@class="title"]') 
	    #loc = driver.find_element_by_xpath('//div[@id="location"]//span[@class="locality"]/a')
	    #industry = driver.find_element_by_xpath('//div[@id="location"]//dd[@class="industry"]/a')
	    #current = driver.find_element_by_xpath('//tr[@id="overview-summary-current"]//td')
	    print name + ";"+ crystal.text # ";"+ loc.text + ";" + tit.text + ";" + crystal.text
    except Exception:
        print name +";ERROR;"+ str(Exception)
        return False		

    return True

def process_messages(fname, text_fname):
    text = open(text_fname).read().strip()
    text = text.decode('utf8')
    driver = get_driver()
    driver.get(DIALOG_URL)
    time.sleep(5)
    for name, position in csv.reader(open(fname)):
        try:
            name = name.decode('utf8')
            position = position.decode('utf8')
            #_, _, exist = get_dialog_status(driver, name)
            #if exist:
            #    print 'canceled, dialog exist', name
            #    continue
			
            sent = False
            while not sent:
                sent = send_msg(driver, name, text.format(name=name, position=position))
                time.sleep(3)
			
        except Exception as e:
            logging.exception('exc')
            print 'failed, error={}'.format(e.message), name
            time.sleep(3)
            driver.get(DIALOG_URL)
            time.sleep(3)

if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    subparsers = parser.add_subparsers(dest='action')
    group1 = subparsers.add_parser('con', help='get conversations')
    group1.add_argument('input', help='getting dialogs, input - list of users')

    group2 = subparsers.add_parser('send', help='send msg')
    group2.add_argument('text', help='text of msg')
    group2.add_argument('input', help='list of users')

    args = parser.parse_args()
    if args.action == 'send':
        process_messages(args.input, args.text)
