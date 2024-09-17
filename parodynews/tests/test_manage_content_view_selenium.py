from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the WebDriver
driver = webdriver.Chrome()

try:
    # Open the URL
    driver.get('http://127.0.0.1:8000/manage_content/')

    # Find the form fields and fill them out
    content_detail_id_field = driver.find_element(By.NAME, 'content_detail_id')
    content_detail_id_field.send_keys('1')  # Replace with actual content_detail_id

    # Add other necessary fields for ContentItemForm
    field1 = driver.find_element(By.NAME, 'field1')
    field1.send_keys('value1')

    field2 = driver.find_element(By.NAME, 'field2')
    field2.send_keys('value2')

    # Set the _method field to 'save'
    method_field = driver.find_element(By.NAME, '_method')
    method_field.send_keys('save')

    # Submit the form
    method_field.send_keys(Keys.RETURN)

    # Wait for the response and check the result
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

    # Print the response
    print(driver.page_source)

finally:
    # Close the WebDriver
    driver.quit()