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
DIALOG_URL = 'https://www.linkedin.com/messaging/'


EMAIL = "ize.com"
PASSWORD = "ism07"


def get_driver():
    driver = webdriver.Firefox()
    time.sleep(1)
    driver.get('https://www.linkedin.com')
    driver.find_element_by_id('login-email').send_keys(EMAIL)
    driver.find_element_by_id('login-password').send_keys(PASSWORD)
    driver.find_element_by_id('login-password').send_keys('\n')
    time.sleep(1)
    return driver



#
JSCODE = "return $.ajax({url: '/messaging/conversationsView', async: false, data: {keyword: '%s'}}).responseText"



def get_dialog_status(driver, name):
    ret = driver.execute_script(JSCODE % name)
    resp = json.loads(ret)
    parts = [c['participants'][0] for c in resp['conversationsBefore']]
    names = [u'{} {}'.format(i['firstName'], i['lastName']) for i in parts]
    return name, ','.join(names), name in names


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
    driver.find_element_by_id('compose-button').click()
    name_input = driver.find_element_by_xpath('//input[@id="pillbox-input"]')
    name_input.click()
    name_input.clear()
    name_input.send_keys(Keys.DELETE*20)
    name_input.send_keys(Keys.BACKSPACE*20)
    name_input.send_keys(name)
    time.sleep(2)
    name_input.send_keys('\n')

    try:
        found_name = driver.find_element_by_xpath('//ul[@id="pillbox-list"]/li/span').text
    except exceptions.NoSuchElementException:
        print 'failed, no name', name
        return

    if name!=found_name:
        print 'failed, not same name', name, found_name
        return
    text_input = driver.find_element_by_xpath('//textarea[@id="compose-message"]')
    text_input.clear()
    text = text.split('\n')
    for tx in text:
        text_input.send_keys(tx)
        time.sleep(0.1)
        text_input.send_keys(Keys.SHIFT, Keys.ENTER)
    time.sleep(0.2)
    text_input.send_keys(Keys.ENTER)
    time.sleep(1)
    try:
        text_input.send_keys(Keys.ENTER)
    except exceptions.StaleElementReferenceException:
        pass
    return True

def process_messages(fname, text_fname):
    text = open(text_fname).read().strip()
    text = text.decode('utf8')
    driver = get_driver()
    driver.get(DIALOG_URL)
    time.sleep(5)
	number = 1
    for name, position in csv.reader(open(fname)):
        try:
            name = name.decode('utf8')
            position = position.decode('utf8')
            _, _, exist = get_dialog_status(driver, name)
            #if exist:
            #    print 'canceled, dialog exist', name
            #    continue
            sent = send_msg(driver, name, text.format(name=name, position=position))
            if sent:
                print number, 'sent', name
				number = number + 1
				
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
    if args.action == 'con':
        process_dialog(args.input)
    elif args.action == 'send':
        process_messages(args.input, args.text)

# send ./msg.txt  ./input.csv
