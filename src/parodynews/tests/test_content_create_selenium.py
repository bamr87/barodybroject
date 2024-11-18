from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
driver.get('http://localhost:8000/content/')
# Wait until the content form is present
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'content_form')))

# Fill out the content creation form
title_field = driver.find_element(By.NAME, 'title')
description_field = driver.find_element(By.NAME, 'description')
author_field = driver.find_element(By.NAME, 'author')

title_field.send_keys('Test Content')
description_field.send_keys('Test Description')
author_field.send_keys('Test Author')

# Submit the form
submit_button = driver.find_element(By.ID, 'save-button')
submit_button.click()

# Verify that the content was created successfully
WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Content and its details saved successfully!'))

# Close the browser
driver.quit()