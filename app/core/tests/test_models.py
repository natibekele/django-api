from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email = 'test@londev.com', password= 'password'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@lchekit.org'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """ Test the email for a new user is normalized"""
        email = 'test@JKCODING.ORG'
        user = get_user_model().objects.create_user(email, 'password')

        self.assertEqual(user.email, email.lower())

    def test_email_field_invalid(self):
        """ Test creating user with no email raises error, \
            doesn't check if email is valid"""
        with self.assertRaises(ValueError):
            email = None
            get_user_model().objects.create_user(email, 'password')

    def test_create_super_user(self):
        """ Test that a superuser is created, isStaff = true"""
        user = get_user_model().objects.create_superuser(
            'test@more.com',
            'password'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self): 
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user= sample_user(),
            name = 'Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes= 5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_image_file_name(self, mock_uuid):
        """Test that image is saved in the correct loaction"""
        uuid='my-test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(exp_path,file_path)


