import threading
import time
import unittest
from unittest import TestCase
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import runpy
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from config import TestConfig
from models import Friend, User, UserStat, Tournament, TournamentPlayer, TournamentResult, Match, Round, Invite


localHost = "http://localhost:5000/"

def generate_database():
    runpy.run_module("generate_test_db", run_name="__main__")

class SeleniumTestCase(TestCase):
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        generate_database()

        self.server_process = multiprocessing.Process(target=self.testApp.run)
        self.server_process.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(localHost)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.server_process.terminate()
        self.driver.close()

    def test_login(self):
        driver = self.driver
        print("Starting test_login")
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys("ChrisL")
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.assertEqual("Login successful!", 
                        driver.find_element(By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='TourneyPro Dashboard'])[1]/following::div[2]").text)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

if __name__ == '__main__':
    unittest.main()