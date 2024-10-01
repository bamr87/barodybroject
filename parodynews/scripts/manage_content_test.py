import requests
from bs4 import BeautifulSoup

# Define the URL for the ManageContentView
url = 'http://127.0.0.1:8000/content/'

# Start a session to persist cookies
session = requests.Session()

# Fetch the CSRF token by making a GET request to the form page
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

# Define the data to be sent in the POST request
data = {
    '_method': 'create',  # This will invoke the save method in ManageContentView
    'title': 'Example Title',
    'description': 'Example Description',
    'csrfmiddlewaretoken': csrf_token,  # Include the CSRF token
    # Add other necessary fields here
}

# Optionally, add headers if needed (e.g., for authentication)
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

# Send the POST request
response = session.post(url, data=data, headers=headers)

# Check the response
if response.status_code == 200:
    try:
        print('Request was successful')
        print(response.json())  # Try to parse JSON
    except requests.exceptions.JSONDecodeError:
        print('Response is not in JSON format')
        print(response.text)  # Print raw text
else:
    print(f'Failed to send request: {response.status_code}')
    print(response.text)