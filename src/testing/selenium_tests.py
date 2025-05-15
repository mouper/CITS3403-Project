import threading
import time
import unittest
from unittest import TestCase
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
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
from generate_test_db import init_db, populate_data

localHost = "http://localhost:5000/"

def generate_database():
    init_db()
    populate_data()

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
        # Add window size to ensure consistent viewport
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)  # Increase default wait time
        self.driver.get(localHost)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.server_process.terminate()
        self.driver.close()

    def scroll_to_element(self, element):
        """Helper method to scroll element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # Add a small wait after scrolling
        time.sleep(0.5)

    def click_element(self, element):
        """Helper method to scroll to element and click it"""
        self.scroll_to_element(element)
        element.click()

    def test_login(self):
        driver = self.driver
        wait = self.wait
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys("ChrisL")
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"]").click()
        time.sleep(2)
        self.assertEqual("Login successful!", driver.find_element(By.CSS_SELECTOR, "div.alert.alert-success").text)
    
    def test_logout(self):
        driver = self.driver
        wait = self.wait
        
        # Login process
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys("ChrisL")
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"]").click()
        time.sleep(2)
        
        # Navigate to account page
        driver.get("http://127.0.0.1:5000/dashboard")
        account_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[4]/span[2]")))
        self.click_element(account_link)
        
        # Click logout - using explicit scroll since it's at bottom of page
        driver.get("http://127.0.0.1:5000/account")
        logout_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))
        driver.execute_script("arguments[0].scrollIntoView(true);", logout_link)
        time.sleep(2)  # Small wait for scroll to complete
        self.driver.find_element(By.LINK_TEXT, "Logout").click()
        
        # Verify logout
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/?fresh=1", self.driver.current_url)

    def test_navbar(self):
        driver = self.driver
        wait = self.wait
        
        # Wait for login link and click
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys("ChrisL")
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"]").click()
        time.sleep(2)
        
        # Wait for redirect and check dashboard
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/dashboard", self.driver.current_url)
        
        # Navigate to Analytics
        analytics_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Analytics")))
        self.click_element(analytics_link)
        
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/analytics", self.driver.current_url)
        
        # Navigate to Requests
        requests_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[3]/span[2]")))
        self.click_element(requests_link)
        
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/requests", self.driver.current_url)
        
        # Navigate to Account
        account_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[4]/span[2]")))
        self.click_element(account_link)
        
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/account", self.driver.current_url)

    def test_landing_links(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.CSS_SELECTOR, "a.herobtn-base.herobtn-signup.medium1").click()
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/signup", self.driver.current_url)
        driver.find_element(By.XPATH, "//p/a").click()
        time.sleep(2)
        self.assertIn("http://127.0.0.1:5000/login", self.driver.current_url)

        
if __name__ == '__main__':
    unittest.main()