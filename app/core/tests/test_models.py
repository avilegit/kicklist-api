from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email = 'test@testdomain.com', password = "testpassword"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_email_succesful(self):
        """Test creating a new user with email is succesful"""
        email = 'test@testdomain.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        email = 'test@TESTDOMAIN.COM'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises error"""

        with self.assertRaises(ValueError):
            password = 'testpassword'
            user = get_user_model().objects.create_user(
                email = None,
                password = password
            )
    def test_create_new_superuser(self):
        """Test creating a new super user"""

        email = 'test@testdomain.com'
        password = 'testpassword'
        user = get_user_model().objects.create_superuser(
            email = email,
            password = password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Runners'
        )

        self.assertEqual(str(tag), tag.name)
    
    def test_characteristics_str(self):
        """Test the characteristic string representation"""
        characteristic = models.Characteristic.objects.create(
            user = sample_user(),
            name = 'suede'
        )
        
        self.assertEqual(str(characteristic), characteristic.name)

    def test_shoes_str(self):
        """Test the shoes string representation"""
        shoes = models.Shoes.objects.create(
            user = sample_user(),
            title = 'Airmax 90',
            brand = 'Nike',
            price = '160'
        )

        self.assertEqual(str(shoes), shoes.title)

    @patch('uuid.uuid4')
    def test_shoe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.shoe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/shoe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

