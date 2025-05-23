import threading
import time
import unittest
from unittest import TestCase
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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

        # Create and start server in a thread
        self.server = make_server('localhost', 5000, self.testApp)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        # Add window size to ensure consistent viewport
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)  # Increase default wait time
        self.driver.get(localHost)

    def tearDown(self):
        self.driver.quit()
        # Shutdown server and join thread
        self.server.shutdown()
        self.server_thread.join()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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
        
        # Login process
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
        analytics_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[2]/span[2]")))
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

    def test_profile_update(self):
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
        account_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[4]/span[2]")))
        self.click_element(account_link)
        
        # Find and test winrate section
        winrate = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.medium4")))
        driver.execute_script("arguments[0].scrollIntoView(true);", winrate)
        time.sleep(2)  # Small wait for scroll to complete
        
        self.assertEqual("Win Rate", winrate.text)
        
        # Test toggle switch
        toggle_label = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "label.switch")))
        self.assertEqual("Hidden", toggle_label.text)
        
        # Click toggle and verify change
        toggle = driver.find_element(By.XPATH, "//label/span")
        self.click_element(toggle)
        self.assertEqual("Shown", toggle_label.text)
        
        # Save changes and verify alert
        save_btn = wait.until(EC.element_to_be_clickable((By.ID, "save-stats-btn")))
        self.assertEqual("Save Changes", save_btn.text)
        save_btn.click()
        
        # Wait for and verify alert
        time.sleep(2)
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()

        self.driver.refresh()
        time.sleep(2)
        # Verify winrate is now shown
        winrate_value = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.winrate")))
        self.assertTrue(winrate_value.text.endswith("WR"), "Winrate should end with 'WR'")

    def test_discard_tournament(self):
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

        # Create tournament
        create_tournament = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Create New Tournament")))
        self.assertEqual("Create New Tournament", create_tournament.text)
        create_tournament.click()

        # Fill tournament details
        driver.get("http://127.0.0.1:5000/new_tournament")
        time.sleep(2)  # Wait for page load
        
        # Tournament name
        tournament_name = driver.find_element(By.ID, "tournamentName")
        tournament_name.click()
        tournament_name.clear()
        tournament_name.send_keys("SeleniumTestTourney")
        
        # Round time limit
        round_time = Select(driver.find_element(By.ID, "roundTimeLimit"))
        round_time.select_by_visible_text("10 minutes")
        
        # Tournament type
        tournament_type = Select(driver.find_element(By.ID, "tournamentType"))
        tournament_type.select_by_visible_text("Round Robin")
        
        # Game type
        game_type = Select(driver.find_element(By.ID, "gameType"))
        game_type.select_by_visible_text("Pokémon TCG")
        
        # Competitor count
        competitor_count = Select(driver.find_element(By.ID, "competitorCount"))
        competitor_count.select_by_visible_text("2")
        time.sleep(1)

        discardTournament = wait.until(EC.element_to_be_clickable((By.ID, "discardTournament")))
        discardTournament.click()
        
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        self.assertIn("Are you sure you want to discard this tournament? Any unsaved changes will be lost.", alert.text)
        alert.accept()
        
        time.sleep(2)
        # Check if tournament name field is empty
        tournament_name = driver.find_element(By.ID, "tournamentName")
        self.assertEqual("", tournament_name.get_attribute("value"), "Tournament name field should be empty")

        # Check if Round time limit field is empty
        roundTimeLimit = driver.find_element(By.ID, "roundTimeLimit")
        self.assertEqual("", roundTimeLimit.get_attribute("value"), "Round time limit field should be empty")

    def test_accept_friend_request(self):
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

        # Navigate to requests page
        requests_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[3]/span[2]")))
        self.click_element(requests_link)
        time.sleep(2)

        self.assertEqual("Decline", driver.find_element(By.CSS_SELECTOR, "button[name=\"response\"]").text)
        self.assertEqual("Accept", driver.find_element(By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='MorganW'])[1]/following::button[2]").text)

        accept = wait.until(EC.element_to_be_clickable((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='MorganW'])[1]/following::button[2]")))
        self.click_element(accept)
        time.sleep(2)

        # Navigate to dashboard page
        dashboard = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a/span[2]")))
        self.click_element(dashboard)
        time.sleep(2)

        self.assertEqual("MorganW", driver.find_element(By.XPATH,"//li[6]").text)
        
    def test_analytics_toggle(self):
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

        # Navigate to analytics page
        analytics_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='mobile-menu']/a[2]/span[2]")))
        self.click_element(analytics_link)
        time.sleep(2)
        
        selector = wait.until(EC.element_to_be_clickable((By.ID, "viewSelector")))
        Select(selector).select_by_visible_text("Admin View")

        time.sleep(2)
        self.assertEqual("Recent Tournaments", driver.find_element(By.XPATH, "//div[@id='adminView']/div/h2").text)

        selector = wait.until(EC.element_to_be_clickable((By.ID, "viewSelector")))
        Select(selector).select_by_visible_text("Player Stats")

        time.sleep(2)
        self.assertEqual("Top Three Tournaments", driver.find_element(By.XPATH, "//div[@id='playerView']/h2").text)
        self.assertEqual("Recent Tournaments", driver.find_element(By.XPATH, "//div[@id='playerView']/h2[2]").text)

    def test_send_friend_request(self):
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

        search = wait.until(EC.presence_of_element_located((By.ID, "playerSearch")))
        driver.execute_script("arguments[0].scrollIntoView(true);", search)
        time.sleep(2)  # Small wait for scroll to complete
        search.click()
        search.clear()
        search.send_keys("RileyG")
        time.sleep(1)

        autofill = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='searchResults']/div")))
        autofill.click()
        time.sleep(2)

        sendBtn = wait.until(EC.element_to_be_clickable((By.ID, "sendInviteBtn")))
        sendBtn.click()

        # Wait for alert to be present and handle it
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        self.assertEqual("Friend request sent!", alert.text)
        alert.accept()

    def test_view_friend_profile(self):
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

        friend_element = wait.until(EC.presence_of_element_located((By.XPATH,"//li")))
        driver.execute_script("arguments[0].scrollIntoView(true);", friend_element)
        self.assertEqual("JD", friend_element.text)
        time.sleep(2)
        friend_element.click()
        time.sleep(2)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.username")))
        self.assertEqual("JD", driver.find_element(By.CSS_SELECTOR, "div.username").text)
        time.sleep(2)

        close = driver.find_element(By.CSS_SELECTOR, "span.close-btn.justify-items-end > svg.close-icon")
        time.sleep(2)
        close.click()

    def test_navigate_tournaments(self):
        driver = self.driver
        wait = self.wait

        # Login process
        driver.get("http://127.0.0.1:5000/")
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys("EventMaster")
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"]").click()
        time.sleep(2)

        # Check draft tournament
        status_filter = wait.until(EC.element_to_be_clickable((By.ID, "statusFilter")))
        Select(status_filter).select_by_visible_text("Draft (Creator)")
        time.sleep(2)
        
        tournament_name = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='adminStatcards']/div/div[2]")))
        self.assertEqual("YuGiOh Weekend Challenge", tournament_name.text)

        # Switch to in-progress tournament
        status_filter = wait.until(EC.element_to_be_clickable((By.ID, "statusFilter")))
        Select(status_filter).select_by_visible_text("In Progress (Creator)")
        
        # Get initial round number
        progress_text = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='adminStatcards']/div/div/p")))
        initial_round = int(progress_text.text.split(" / ")[0])
        self.assertEqual(f"{initial_round} / 4 Rounds", progress_text.text)
        
        view_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "View")))
        view_button.click()

        # Navigate to tournament page
        driver.get("http://127.0.0.1:5000/tournament/13")
        time.sleep(2)

        # Verify tournament elements
        tournament_title = wait.until(EC.presence_of_element_located((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='My Account'])[1]/following::span[1]")))
        self.assertEqual("Pokémon TCG League", tournament_title.text)

        reset_btn = wait.until(EC.presence_of_element_located((By.ID, "resetRoundBtn")))
        self.assertEqual("Reset Round", reset_btn.text)

        save_btn = wait.until(EC.presence_of_element_located((By.ID, "saveExitBtn")))
        self.assertEqual("Save & Exit", save_btn.text)

        end_round_btn = wait.until(EC.presence_of_element_located((By.ID, "endRoundEarlyBtn")))
        driver.execute_script("arguments[0].scrollIntoView(true);", end_round_btn)
        time.sleep(2)
        self.assertEqual("End Round Early", end_round_btn.text)

if __name__ == '__main__':
    unittest.main()