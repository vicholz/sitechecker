#!/usr/bin/env python3

import argparse
import json
import logging
import logging.config
import math
import os
import random
import shutil
import time
import warnings
warnings.filterwarnings('ignore')

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager

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
        if verbose:
            options.add_argument("--verbose")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        #options.add_argument(f'--user-agent="{self.data.get("properties").get("useragent")}"')
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920x1080")
        options.add_argument("--window-position=0,0")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        #options.add_argument("--disable-extensions")
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option('useAutomationExtension', True)
        #options.binary_location = shutil.which("google-chrome-stable")
        
        service = Service(
            executable_path = shutil.which("chromedriver")
        )
        # self.driver = webdriver.Chrome(
        #     service = service,
        #     options = options
        # )
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(1)
        self.verificationErrors = []
        self.accept_next_alert = True
        #self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        #self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": f'{self.data.get("properties").get("useragent")}'})
    
    def get(self, url, **kwargs):
        url = os.path.expandvars(url) 
        logging.debug(f"Getting '{url}'...")
        self.driver.get(url)
        logging.debug(f"Getting '{url}'...DONE!")

    def post(self, url, headers, data, **kwargs):
        url = os.path.expandvars(url) 
        logging.debug(f"Posting to '{url}'...")
        self.driver.request('POST', url, data)
        logging.debug(f"Posting to '{url}'...DONE!")
    
    def find_element(self, selector:str, by=By.ID, timeout:int=10, tries:int=3, **kwargs):
        logging.debug(f"Looking for element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = self.driver.find_element(by, selector)
                logging.debug(f"Looking for visible element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def is_visible(self, selector:str, by=By.ID, timeout:int=10, tries:int=3, **kwargs):
        logging.debug(f"Looking for visible element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = self.driver.find_element(by, selector)
                #e = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, selector)))
                # waiter = WebDriverWait(self.driver, timeout)
                # e = waiter.until(EC.visibility_of_element_located(e))
                logging.debug(f"Looking for visible element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
    
    def is_clickable(self, selector:str, by=By.ID, timeout:int=1, tries:int=3, **kwargs):
        logging.debug(f"Looking for clickable element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = self.driver.find_element(by, selector)
                #e = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, selector)))
                # waiter = WebDriverWait(self.driver, timeout)
                # waiter.until(EC.element_to_be_clickable((by, selector)))
                logging.debug(f"Looking for clickable element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")

    def exists(self, selector:str, by=By.ID, timeout:int=1, tries:int=3, **kwargs):
        logging.debug(f"Looking for element '{selector}'...")
        tries_left = tries
        while tries_left > 0:
            tries_left -= 1
            try:
                e = self.driver.find_element(by, selector)
                # waiter = WebDriverWait(self.driver, timeout)
                # waiter.until(EC.element_to_be_clickable((by, selector)))
                logging.debug(f"Looking for element '{selector}'...DONE!")
                return e
            except:
                logging.error(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")
                time.sleep(timeout)
        raise TimeoutException(f"Timed out waiting for element with '{by}': '{selector}' ({tries_left}/{tries} tries left)")

    def has_inner_text(self, element, value, **kwargs):
        logging.debug(f"Checking element '{element.get('selector')}' has text '{value}'...")
        e = self.is_visible(**element)
        
        if value in e.get_attribute('innerText'):
            logging.debug(f"Checking element '{element.get('selector')}' has text '{value}'...DONE!")
        else:
            error = f"Checking element '{element.get('selector')}' has text '{value}'...NOT FOUND!"
            logging.error(error)
            raise Exception(error)

    def click(self, selector, by, timeout=1, **kwargs):
        logging.debug(f"Clicking element '{selector}'...")
        e = self.is_clickable(selector, by, timeout)
        ActionChains(self.driver).move_to_element(e).click(e).perform()
        logging.debug(f"Clicking element '{selector}'...DONE!")

    def click_and_hold(self, selector, by, timeout, seconds=[1], fail=True, **kwargs):
        logging.debug(f"Clicking and h olding element '{selector}'...")
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
        logging.debug(f"Clicking and holding element '{selector}'...DONE!")

    def send_enter(self, selector, by, timeout=1, **kwargs):
        logging.debug(f"Sending ENTER to element '{selector}'...")
        e = self.driver.find_element(by, selector)
        e.send_keys(Keys.ENTER)
        logging.debug(f"Sending ENTER to element '{selector}'...DONE!")

    def send(self, element, value, **kwargs):
        logging.debug(f"Sending value to element '{element.get('selector')}'...")
        e = self.is_clickable(**element)
        e.clear()
        e.send_keys(value)
        logging.debug(f"Sending value to element '{element.get('selector')}'...DONE!")

    def send_var(self, element, var_name, **kwargs):
        logging.debug(f"Sending '{var_name}' to '{element.get('selector')}'...")
        e = self.is_clickable(**element)
        e.clear()
        e.send_keys(os.environ.get(f"{var_name}", ""))
        logging.debug(f"Sending '{var_name}' to '{element.get('selector')}'...DONE!")

    def export_attrib_value(self, element, attrib, var_name, **kwargs):
        logging.debug(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute(attrib).strip()
        logging.debug(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.debug(f"Setting ENV var '{var_name}' = '{value}'...")
        os.environ[var_name] = value
        logging.debug(f"Setting ENV var '{var_name}' = '{value}'...DONE!")

    def export_text(self, element, target_var_name, **kwargs):
        logging.debug(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute("innerText").strip()
        logging.debug(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.debug(f"Setting ENV var '{target_var_name}' = '{value}'...")
        os.environ[target_var_name] = value
        logging.debug(f"Setting ENV var '{target_var_name}' = '{value}'...DONE!")
    
    def write_attrib_value(self, element, attrib, file, **kwargs):
        logging.debug(f"Getting element value from '{element.get('selector')}'...")
        value = self.find_element(**element).get_attribute(attrib).strip()
        logging.debug(f"Getting element value from '{element.get('selector')}'...DONE!")
        logging.debug(f"Writting '{value}' to '{file}'...")
        with open(file, "w") as f:
            f.write(value)
            f.close()
        logging.info(f"Writting '{value}' to '{file}'...DONE!")
    
    def read_file_value(self, file, target_var_name, **kwargs):
        logging.debug(f"Reading file '{file}' to ENV var '{target_var_name}'...")
        with open(file, "r") as f:
            value = f.read()
            f.close()
        os.environ[target_var_name] = value
        logging.debug(f"Reading file '{file}' to ENV var '{target_var_name}'...DONE!")

    def scroll(self, x=0, y=0, **kwargs):
        logging.debug(f"Scrolling x = {x}, y = {y}...")
        self.driver.execute_script(f"window.scrollBy({x},{y})", "")
        logging.debug(f"Scrolling x = {x}, y = {y}...DONE!")

    def sleep(self, seconds=1, **kwargs):
        logging.debug(f"Sleeping for {seconds} seconds...")
        time.sleep(seconds)
        logging.debug(f"Sleeping for {seconds} seconds...DONE!")

    def move_mouse(self, x_offset, y_offset, **kwargs):
        logging.debug(f"Moving mouse x = {x_offset}, y = {y_offset}...")
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(x_offset, y_offset)
        action.perform()
        logging.debug(f"Moving mouse x = {x_offset}, y = {y_offset}...DONE!")

    def random_mouse_moves(self, x_max=10, y_max=10, **kwargs):
        x = math.floor(random.random() * x_max) + 1
        y = math.floor(random.random() * y_max) + 1
        logging.debug(f"Moving mouse x = {x}, y = {y}...")
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(x, y)
        action.perform()
        logging.debug(f"Moving mouse x = {x}, y = {y}...DONE!")

    def submit_form(self, selector, by, timeout=1, **kwargs):
        logging.debug(f"Submitting form '{selector}'...")
        e = self.exists(selector, by, timeout)
        e.submit()
        logging.debug(f"Submitting form '{selector}'...DONE!")

    def execute_script(self, script, **kwargs):
        logging.debug(f"Executing script '{script}'...")
        self.driver.execute_script(script)
        logging.debug(f"Executing script '{script}'...DONE!")

    def execute_task(self, task):
        if not task in list(self.data.get("execution")):
            raise Exception(f"Task '{task}' not found in exection list. Exiting.")
        if not task in list(self.data.get("tasks")):
            raise Exception(f"Task '{task}' is not defined. Exiting.")
        t = self.data.get("tasks").get(task)
        for action_obj in t:
            action = action_obj.get("action")
            params = dict(action_obj)
            desc = action_obj.get("desc", "NO DESC")
            del params['action']
            if hasattr(self, action) and callable(getattr(self, action)):
                logging.info(f"[{task}] Executing action '{action}' - {desc}...")
                if os.path.exists(f"{task}-{action}-before.png"): os.remove(f"{task}-{action}-before.png")
                if os.path.exists(f"{task}-{action}-after.png"): os.remove(f"{task}-{action}-after.png")
                task_index = self.data.get("tasks").get(task).index(action_obj)
                task_name = task.replace(" ", "_")
                task_action = action.replace(" ", "_")
                self.driver.save_screenshot(f"screenshots/{task_name}-{task_index:03}-00-{task_action}-before.png")
                getattr(self, action)(**params)
                self.driver.save_screenshot(f"screenshots/{task_name}-{task_index:03}-01-{task_action}-after.png")
                logging.info(f"[{task}] Executing action '{action}' - {desc}...DONE!")
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
