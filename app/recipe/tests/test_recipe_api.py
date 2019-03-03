from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe,Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

# /api/recipe/recipes
# /api/reciep/recipies/1/

def sample_recipe(user,**params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user,**defaults)

def sample_tag(user,name='Main Course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user,name='OJ'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user,name=name)

class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe API success"""

    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='yoyoyo@ttt.com',
            password='password'
        )
        self.client.force_authenticate(self.user)

    
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
    

    def test_retrieve_recipes_for_authenticated_user(self):
        """Test only retrieving users recipes"""
        user2 = get_user_model().objects.create_user(
            email='hh@333.com',
            password='hhh'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user2)
        recipes = Recipe.objects.all().filter(user=self.user)
        res = self.client.get(RECIPES_URL)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    
    def test_view_recipe_detail(self):
        """Test viewming a recipe detail"""
        recipe=sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialzer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serialzer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

