import requests
from bs4 import BeautifulSoup

# Define the URL for the ManageContentView
url = "http://127.0.0.1:8000/content/"

# Start a session to persist cookies
session = requests.Session()

# Fetch the CSRF token by making a GET request to the form page
response = session.get(url)
soup = BeautifulSoup(response.content, "html.parser")
csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

# Login credentials
login_data = {
    "username": "testuser",
    "password": "testpassword",
    "csrfmiddlewaretoken": csrf_token,
}

# Perform login
login_url = "http://127.0.0.1:8000/login/"
session.post(login_url, data=login_data)

# Define the data to be sent in the POST request
data = {
    "_method": "save",
    "title": "Test Content",
    "description": "Test Description",
    "author": "Test Author",
    "csrfmiddlewaretoken": csrf_token,
    # ...additional required fields...
}

# Optionally, add headers if needed (e.g., for authentication)
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

# Send the POST request to create content
response = session.post(url, data=data)

# Check the response
if response.status_code == 302:
    print("Content created successfully")
else:
    print(f"Failed to create content: {response.status_code}")
    print(response.text)
