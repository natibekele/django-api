from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGERDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_requried(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(INGERDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """test ingredients can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@me.com',
            password='password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(name='correander', user=self.user)
        Ingredient.objects.create(name='nutmeg', user=self.user)

        res =self.client.get(INGERDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many= True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    
    def test_ingredients_limited_to_authenticated_user(self):
        """Test that the ingredients are limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='test@eee.com',
            password='pass'
        )
        ingredient = Ingredient.objects.create(user=self.user, name='pork',)
        Ingredient.objects.create(user=user2, name='salt')

        res = self.client.get(INGERDIENTS_URL)

        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """Test creating an ingredient"""


