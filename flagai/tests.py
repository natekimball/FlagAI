from django.test import Client, TestCase
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import File
from .models import Report

class AdminLoginTestCase(TestCase):
    def setUp(self):
        # Create a superuser for testing
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpassword')

    def test_valid_admin_login(self):
        # Create a client
        client = Client()

        # Attempt to login with valid admin credentials
        response = client.post('/admin/login/', {'username': 'admin', 'password': 'adminpassword'})

        # Check if the user is redirected to the admin page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class FlagaiViewsTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpassword')
    
    def test_index_view(self):
        # Create a client
        client = Client()

        # Log in
        client.login(username='testuser', password='testpassword')

        # Attempt to access the index page after logging in
        response = client.get('/')

        # Check if the user is able to access the index page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flagai/common_index.html')

    def test_validate_site_admin_login(self):
        client = Client()
        self.user = User.objects.create_user(username='testuseradmin', email='cs3240.super@gmail.com',
                                             password='testpasswordadmin')

        client.login(username='testuseradmin', password='testpasswordadmin')

        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flagai/admin_index.html')

    def test_user_logout(self):
        self.client.logout()
        response = self.client.get(reverse('flagai:logout'))
        self.assertEqual(response.status_code, 302)


class FlagaiAdminViewsTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpassword')
        group, created = Group.objects.get_or_create(name='site_admin')
        self.user.groups.add(group)

    def test_index_view(self):
        # Create a client
        client = Client()

        # Log in
        client.login(username='testuser', password='testpassword')

        # Attempt to access the index page after logging in
        response = client.get('/')

        # Check if the user is able to access the index page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flagai/admin_index.html')


class ReportCreationTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpassword')
    
    def test_report_creation_and_view(self):
        # Create a client
        client = Client()

        # Log in
        client.login(username='testuser', password='testpassword')

        test_file = SimpleUploadedFile('test.txt', b'test content')
        file = File(name='test.txt', file=test_file)
        response = client.post('/reports/create/', {
            'description': 'Test description',
            'offender_link': 'http://example.com',
            'people_involved': 'Test person',
            'contact_email': 'test@test.com',
            'feedback': 'Test feedback',
            'file_upload': file,
        })

        # Check if the report was created successfully
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        self.assertTrue(Report.objects.filter(description='Test description').exists())


class ReportDeleteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Create mock report
        response = self.client.post('/reports/create/', {
            'description': 'Test description',
            'offender_link': 'http://example.com',
            'people_involved': 'Test person',
            'contact_email': 'test@test.com',
            'feedback': 'Test feedback',
        })

    def test_delete_report(self):
        response = self.client.get(reverse('flagai:delete_report', args=[1]))
        self.assertEqual(response.status_code, 302)


class ReportSubmittedTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Create mock report
        test_file = SimpleUploadedFile('test.txt', b'test content')
        file = File(name='test.txt', file=test_file)
        response = self.client.post('/reports/create/', {
            'description': 'Test description',
            'offender_link': 'http://example.com',
            'people_involved': 'Test person',
            'contact_email': 'test@test.com',
            'feedback': 'Test feedback',
            'file_upload': file
        })

    def test_profile_view(self):
        response = self.client.get(reverse('flagai:profile'))
        self.assertEqual(response.status_code, 200)

    def test_create_report_view(self):
        response = self.client.get(reverse('flagai:create_report'))
        self.assertEqual(response.status_code, 200)

