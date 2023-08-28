#!/usr/bin/env python3

import argparse
import json
import logging
import logging.config
import math
import os
import random
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
    def __init__(self, data, verbose=False):
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
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service_args = [
            '--ssl-protocol=any',
            '--ignore-ssl-errors=true'
        ]

        if not verbose:
            options.add_argument('--headless')
            service_args.append("--headless")

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
    
    def find_element(self, selector:str, by=By.ID, timeout:int=10, tries:int=3):
        logging.info(f"Looking for element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = self.driver.find_element(by, selector)
                logging.info(f"Looking for visible element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def is_visible(self, selector:str, by=By.ID, timeout:int=10, tries:int=3):
        logging.info(f"Looking for visible element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, selector)))
                # waiter = WebDriverWait(self.driver, timeout)
                # e = waiter.until(EC.visibility_of_element_located(e))
                logging.info(f"Looking for visible element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def is_clickable(self, selector:str, by=By.ID, timeout:int=1, tries:int=3):
        logging.info(f"Looking for clickable element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, selector)))
                # waiter = WebDriverWait(self.driver, timeout)
                # waiter.until(EC.element_to_be_clickable((by, selector)))
                logging.info(f"Looking for clickable element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def has_inner_text(self, element, value):
        logging.info(f"Checking element '{element.get('selector')}' has text '{value}'...")
        e = self.is_visible(**element)
        
        if value in e.get_attribute('innerText'):
            logging.info(f"Checking element '{element.get('selector')}' has text '{value}'...DONE!")
        else:
            error = f"Checking element '{element.get('selector')}' has text '{value}'...NOT FOUND!"
            logging.error(error)
            raise Exception(error)

    def click(self, selector, by, timeout):
        logging.info(f"Clicking element '{selector}'...")
        e = self.is_clickable(selector, by, timeout)
        e.click()
        logging.info(f"Clicking element '{selector}'...DONE!")
    
    def click_and_hold(self, selector, by, timeout, seconds=[1], fail=True):
        logging.info(f"Clicking and holding element '{selector}'...")
        try:
            action = ActionChains(self.driver)
            e = self.is_clickable(selector, by, timeout)
            for s in seconds:
                if type(s) != int:
                    s = eval(s)
                action.click_and_hold(e)
                action.perform()
                self.random_mouse_moves()
                time.sleep(s)
                self.random_mouse_moves()
                action.release(e)
        except Exception as e:
            if fail:
                raise Exception(e)
            else:
                logging.warning(f"Clicking and holding element '{selector}'...Failed! Skipping!")
        logging.info(f"Clicking and holding element '{selector}'...DONE!")

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

    def export_attrib_value(self, element, attrib, var_name):
        logging.info(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute(attrib).strip()
        logging.info(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.info(f"Setting ENV var '{var_name}' = '{value}'...")
        os.environ[var_name] = value
        logging.info(f"Setting ENV var '{var_name}' = '{value}'...DONE!")

    def export_text(self, element, var_name):
        logging.info(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute("innerText").strip()
        logging.info(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.info(f"Setting ENV var '{var_name}' = '{value}'...")
        os.environ[var_name] = value
        logging.info(f"Setting ENV var '{var_name}' = '{value}'...DONE!")
    
    def write_attrib_value(self, element, attrib, file):
        logging.info(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute(attrib).strip()
        logging.info(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.info(f"Writting '{value}' to '{file}'...")
        with open(file, "w") as f:
            f.write(value)
            f.close()
        logging.info(f"Writting '{value}' to '{file}'...DONE!")
    
    def read_file_value(self, element, file, var_name):
        logging.info(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute(attrib).strip()
        logging.info(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.info(f"Reading file '{file}' to ENV var '{var_name}'...")
        with open(file, "r") as f:
            value = f.read()
            f.close()
        os.environ[var_name] = value
        logging.info(f"Reading file '{file}' to ENV var '{var_name}'...DONE!")

    def scroll(self, x=0, y=0):
        logging.info(f"Scrolling x = {x}, y = {y}...")
        self.driver.execute_script(f"window.scrollBy({x},{y})", "")
        logging.info(f"Scrolling x = {x}, y = {y}...DONE!")

    def sleep(self, seconds=1):
        logging.info(f"Sleeping for {seconds} seconds...")
        time.sleep(seconds)
        logging.info(f"Sleeping for {seconds} seconds...DONE!")

    def move_mouse(self, x_offset, y_offset):
        logging.info(f"Moving mouse x = {x_offset}, y = {y_offset}...")
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(x_offset, y_offset)
        action.perform()
        logging.info(f"Moving mouse x = {x_offset}, y = {y_offset}...DONE!")
    
    def random_mouse_moves(self, x_max=10, y_max=10):
        x = math.floor(random.random() * x_max) + 1
        y = math.floor(random.random() * y_max) + 1
        logging.info(f"Moving mouse x = {x}, y = {y}...")
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(x, y)
        action.perform()
        logging.info(f"Moving mouse x = {x}, y = {y}...DONE!")

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
                task_index = list(self.data.get("tasks").get("task")).index(action)
                task_name = task.replace(" ", "_")
                task_action = action.replace(" ", "_")
                self.driver.save_screenshot(f"{task_index:03}-{task_name}-{task_action}-before.png")
                getattr(self, action)(**params)
                self.driver.save_screenshot(f"{task_index:03}-{task_name}-{task_action}-after.png")
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

    sc = SiteChecker(args.data, verbose=args.verbose)
    for task in sc.data.get("execution"):
        sc.execute_task(task)
