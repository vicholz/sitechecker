#!/usr/bin/env python3

import argparse
import json
import logging
import logging.config
import os
import time
import warnings
warnings.filterwarnings('ignore')

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent

class SiteChecker(object):
    def __init__(self, data):
        if os.path.isfile(data):
            with open(data, 'r') as f:
                self.data = json.load(f)
                f.close()
        else:
            self.data = data

        ua = UserAgent()
        user_agent = ua.random
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-agent="{self.data.get("properties").get("useragent")}"')
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service_args = [
            '--ssl-protocol=any',
            '--ignore-ssl-errors=true',
            '--headless'
        ]
        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        # dcap["phantomjs.page.settings.userAgent"] = (self.data.get("properties").get("useragent"))
        # self.driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap)
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(1)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1920, 1080)
        self.verificationErrors = []
        self.accept_next_alert = True
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": f'{self.data.get("properties").get("useragent")}'})
        
    def get(self, url):
        logging.info(f"Getting '{url}'...")
        self.driver.get(url)
        logging.info(f"Getting '{url}'...DONE!")

    def post(self, url, headers, data):
        logging.info(f"Posting to '{url}'...")
        self.driver.request('POST', url, data)
        logging.info(f"Posting to '{url}'...DONE!")
    
    def is_visible(self, selector:str, by=By.ID, timeout:int=1, tries:int=3):
        logging.info(f"Looking for visible element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
                waiter = WebDriverWait(self.driver, timeout)
                waiter.until(EC.visibility_of_element_located((by, selector)))
                logging.info(f"Looking for visible element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def is_clickable(self, selector:str, by=By.ID, timeout:int=1, tries:int=3):
        logging.info(f"Looking for clickable element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))
                waiter = WebDriverWait(self.driver, timeout)
                waiter.until(EC.element_to_be_clickable((by, selector)))
                logging.info(f"Looking for clickable element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def has_inner_text(self, element, value):
        logging.info(f"Checking element '{element.get('selector')}' has text '{value}'...")
        e = self.is_visible(**element)
        assert(e.get_attribute('innerText') == value)
        logging.info(f"Checking element '{element.get('selector')}' has text '{value}'...DONE!")

    def click(self, selector, by, timeout):
        logging.info(f"Clicking element '{selector}'...")
        e = self.is_clickable(selector, by, timeout)
        e.click()
        logging.info(f"Clicking element '{selector}'...DONE!")

    def send(self, element, value):
        logging.info(f"Sending value to element '{element.get('selector')}'...")
        e = self.is_clickable(**element)
        e.clear()
        e.send_keys(value)
        logging.info(f"Sending value to element '{element.get('selector')}'...DONE!")

    def send_var(self, element, var_name):
        logging.info(f"Sending '{var_name}' to '{element.get('selector')}'...")
        e = self.is_clickable(**element)
        e.clear()
        e.send_keys(os.environ.get(f"{var_name}", ""))
        logging.info(f"Sending '{var_name}' to '{element.get('selector')}'...DONE!")

    def sleep(self, seconds):
        logging.info(f"Sleeping for {seconds} seconds...")
        time.sleep(seconds)
        logging.info(f"Sleeping for {seconds} seconds...DONE!")

    def execute_task(self, task):
        if not task in list(self.data.get("execution")):
            raise Exception(f"Task '{task}' not found in exection list. Exiting.")
        if not task in list(self.data.get("tasks")):
            raise Exception(f"Task '{task}' is not defined. Exiting.")
        t = self.data.get("tasks").get(task)
        for action_obj in t:
            action = action_obj.get("action")
            params = dict(action_obj)
            del params['action']
            if hasattr(self, action) and callable(getattr(self, action)):
                logging.info(f"[{task}] Executing '{action}'...")
                if os.path.exists(f"{task}-{action}-before.png"): os.remove(f"{task}-{action}-before.png")
                if os.path.exists(f"{task}-{action}-after.png"): os.remove(f"{task}-{action}-after.png")
                self.driver.save_screenshot(f"{task}-{action}-before.png")
                getattr(self, action)(**params)
                self.driver.save_screenshot(f"{task}-{action}-after.png")
                logging.info(f"[{task}] Executing '{action}'...DONE!")
            else:
                raise Exception(f"Action method for '{action}' is not defined. Exiting.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Site Checker')
    parser.add_argument('--data',
                        required=True,
                        action='store',
                        help="Task data as file or JSON.")
    parser.add_argument('--verbose',
                        dest="verbose",
                        required=False,
                        action='store_true',
                        help='Verbose output.')
    args = parser.parse_args()

    logging.config.fileConfig("logger.conf")
    logging.getLogger().setLevel(logging.INFO)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    sc = SiteChecker(args.data)
    for task in sc.data.get("execution"):
        sc.execute_task(task)
