# Create your tests here.
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .forms import ContentItemForm
from .models import ContentDetail

print("Performing tests...")
class ManageContentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_content(self):
        form_data = {
            'instructions': 'Write a short story',
            'prompt': 'Once upon a time'
        }
        response = self.client.post(reverse('manage_content'), data=form_data)
        
        # Check that the response is a redirect (successful form submission)
        self.assertEqual(response.status_code, 302)
        
        # Check that the content was created in the database
        content_detail = ContentDetail.objects.first()
        self.assertIsNotNone(content_detail)
        self.assertEqual(content_detail.title, 'Default Title')
        self.assertEqual(content_detail.description, 'Default Description')
        self.assertEqual(content_detail.author, 'Default Author')

class ContentFormTestCase(TestCase):
    def test_valid_form(self):
        form_data = {'title': 'Valid Title', 'description': 'Valid Description'}
        form = ContentItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_form(self):
        form_data = {'title': '', 'description': 'Valid Description'}
        form = ContentItemForm(data=form_data)
        self.assertFalse(form.is_valid())

class ContentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
    def test_create_content_api(self):
        url = reverse('content_detail')  # Update with the correct API endpoint name
        data = {
            'title': 'Test Content',
            'description': 'Test Description',
            'author': 'Test Author',
            # ...additional required fields...
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContentDetail.objects.count(), 1)
        self.assertEqual(ContentDetail.objects.get().title, 'Test Content')