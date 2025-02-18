import pytest
import requests

@pytest.fixture(scope='module')
def assistant_id():
    url = 'http://localhost:8000/api/assistants/'
    data = {
        'name': 'API Test',
        'description': 'This is a test assistant.',
        'instructions': 'This is a test instruction.',
        'prompt': 'you are a helpful assistant',
        'model': 1  # Updated from a string to a valid numeric id
    }
    response = requests.post(url, json=data)
    assert response.status_code == 201
    response_data = response.json()
    return response_data['id']

def test_create_assistant(assistant_id):
    # This test ensures that the assistant was created successfully
    url = f'http://localhost:8000/api/assistants/{assistant_id}/'
    response = requests.get(url)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['name'] == 'API Test'
    assert response_data['description'] == 'This is a test assistant.'
    assert response_data['instructions'] == 'This is a test instruction.'
    assert response_data['prompt'] == 'you are a helpful assistant.'
    assert response_data['model'] == 'gpt-4o-mini'

def test_get_assistant(assistant_id):
    # Perform a GET request to retrieve the assistant
    url = f'http://localhost:8000/api/assistants/{assistant_id}/'
    response = requests.get(url)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['id'] == assistant_id
    assert response_data['name'] == 'API Test'
    assert response_data['description'] == 'This is a test assistant.'
    assert response_data['instructions'] == 'This is a test instruction.'
    assert response_data['prompt'] == 'you are a helpful assistant.'
    assert response_data['model'] == 'gpt-4o-mini'

# def test_get_content_items():
#     url = 'http://127.0.0.1:8000/api/content-items/'
#     response = requests.get(url)
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# def test_create_content_item():
#     url = 'http://127.0.0.1:8000/api/content-items/'
#     data = {
#         'prompt': 'Test Content',
#         'content': 'This is a test content.',
#         'detail': 1  # Assuming a ContentDetail with ID 1 exists
#     }
#     response = requests.post(url, json=data)
#     assert response.status_code == 201
#     assert response.json()['prompt'] == 'Test Content'
#     assert response.json()['content'] == 'This is a test content.'

# def test_update_content_item():
#     url = 'http://127.0.0.1:8000/api/content-items/1/'
#     data = {
#         'prompt': 'Updated Content',
#         'content': 'This is updated content.',
#         'detail': 1  # Assuming a ContentDetail with ID 1 exists
#     }
#     response = requests.put(url, json=data)
#     assert response.status_code == 200
#     assert response.json()['prompt'] == 'Updated Content'
#     assert response.json()['content'] == 'This is updated content.'

# def test_delete_content_item():
#     url = 'http://127.0.0.1:8000/api/content-items/1/'
#     response = requests.delete(url)
#     assert response.status_code == 204