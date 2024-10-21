from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the login page
driver.get('http://localhost:8000/login')

# Locate the username and password fields and enter the credentials
username_field = driver.find_element(By.NAME, 'username')
password_field = driver.find_element(By.NAME, 'password')

username_field.send_keys('bamr87')
password_field.send_keys('amr123')

# Locate the login button and click it
login_button = driver.find_element(By.ID, "login-form")
login_button.submit()

# Wait for the login to complete
time.sleep(2)

# Open the content creation page
driver.get('http://localhost:8000/content')
time.sleep(5)

# Locate the form by its ID and submit it
form = driver.find_element(By.ID, 'create-button')
time.sleep(5)
form.submit()

# Wait for a bit to see the result
time.sleep(5)

# Close the browser
driver.quit()