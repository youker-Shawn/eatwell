from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient


from .models import Recipe
from .views import RecipeViewSet
from .serializers import RecipeSerializer

User = get_user_model()


# Create your tests here.
class RecipeAPITest(TestCase):
    """API integration test"""

    def setUp(self):
        self.client = APIClient()
        # use create_user instead of create
        self.test_user = User.objects.create_user(username='test', password='test')
        self.recipe_1 = Recipe.objects.create(
            name="Pizza",
            ingredient="Flour, cheese, tomato sauce",
            step="...",
            user=self.test_user,
        )
        self.recipe_2 = Recipe.objects.create(
            name="Salad",
            ingredient="Lettuce, tomato, cucumber",
            step="...",
            user=self.test_user,
        )
        self.recipe_3 = Recipe.objects.create(
            name="Cake",
            ingredient="Flour, sugar, eggs",
            step="...",
            user=self.test_user,
        )
        self.recipe_other_person = Recipe.objects.create(
            name="其他人的菜谱",
            ingredient="...",
            step="...",
            user=User.objects.create_user(username='other', password='other'),
        )

    def test_get_all_recipes_by_user(self):
        # for passing SessionAuthentication
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('recipe-list'))
        recipes = Recipe.objects.filter(user=self.test_user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, serializer.data)

    def test_get_all_recipes_withot_auth(self):
        response = self.client.get(reverse('recipe-list'))
        # SessionAuthentication returns 403 ,BasicAuthentication returns 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_single_recipe(self):
        self.client.login(username='test', password='test')
        response = self.client.get(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk})
        )
        recipe = Recipe.objects.get(pk=self.recipe_1.pk)
        serializer = RecipeSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_withot_auth(self):
        response = self.client.get(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk})
        )
        # SessionAuthentication returns 403 ,BasicAuthentication returns 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_recipe(self):
        self.client.login(username='test', password='test')
        valid_data = {
            'name': 'Soup',
            'ingredient': 'Water, salt, vegetables',
            'step': '...',
        }
        response = self.client.post(reverse('recipe-list'), data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], valid_data["name"])
        self.assertEqual(response.data["ingredient"], valid_data["ingredient"])
        self.assertEqual(response.data["step"], valid_data["step"])
        self.assertEqual(response.data["user"], self.test_user.pk)

    def test_create_recipe_without_auth(self):
        valid_data = {
            'name': 'Soup',
            'ingredient': 'Water, salt, vegetables',
            'step': '...',
        }
        response = self.client.post(reverse('recipe-list'), data=valid_data)
        # SessionAuthentication returns 403 ,BasicAuthentication returns 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invalid_recipe(self):
        self.client.login(username='test', password='test')
        invalid_data = {'name': '', 'ingredient': 'Nothing'}
        response = self.client.post(reverse('recipe-list'), data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_recipe(self):
        self.client.login(username='test', password='test')
        response = self.client.delete(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        recipe = Recipe.objects.filter(id=self.recipe_1.id).first()
        self.assertIsNone(recipe)

    def test_delete_recipe_without_auth(self):
        response = self.client.delete(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk})
        )
        # SessionAuthentication returns 403 ,BasicAuthentication returns 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_recipe(self):
        self.client.login(username='test', password='test')
        update_data = {
            'name': self.recipe_1.name,
            'ingredient': self.recipe_1.ingredient + ', onion',
            'step': '...',
        }
        response = self.client.put(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk}),
            data=update_data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], update_data["name"])
        self.assertEqual(response.data["ingredient"], update_data["ingredient"])
        self.assertEqual(response.data["step"], update_data["step"])
        self.assertEqual(response.data["user"], self.test_user.pk)

    def test_update_recipe_without_auth(self):
        update_data = {
            'name': self.recipe_1.name,
            'ingredient': self.recipe_1.ingredient + ', onion',
            'step': '...',
        }
        response = self.client.put(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk}),
            data=update_data,
            format='json',
        )
        # SessionAuthentication returns 403 ,BasicAuthentication returns 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_recipe(self):
        self.client.login(username='test', password='test')
        partial_data = {
            'name': self.recipe_1.name + " [new]",
        }
        response = self.client.patch(
            reverse('recipe-detail', kwargs={'pk': self.recipe_1.pk}),
            data=partial_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], partial_data['name'])


class RecipeViewTest(TestCase):
    """View functions unit test"""

    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.recipe_data = {
            "name": "炒饭",
            "ingredient": "米饭，鸡蛋，火腿，青豆",
            "step": "1. 打鸡蛋，加盐搅拌。2. 火腿切小丁，青豆洗净。3. 热锅，倒油，炒鸡蛋。4. 加入米饭，翻炒均匀。5. 加入火腿和青豆，继续翻炒。6. 出锅，盛盘。",
        }
        self.test_user = User.objects.create_user(username='test', password='test')

    def test_create_recipe(self):
        post_data = {"user": self.test_user.pk}
        post_data.update(self.recipe_data)
        request = self.factory.post('/recipes/', post_data, format='json')
        # Force authenticate the request with the user
        force_authenticate(request, user=self.test_user)
        view = RecipeViewSet.as_view({'post': 'create'})
        response = view(request)

        # Assert that the response status code is 201 (created)
        self.assertEqual(response.status_code, 201)
        # Assert that the response data matches the recipe data
        self.assertEqual(response.data, post_data)
        # Assert that a recipe object was created in the database
        self.assertEqual(Recipe.objects.count(), 1)
        # Assert that the recipe object belongs to the user
        self.assertEqual(Recipe.objects.first().user, self.test_user)

    def test_delete_recipe(self):
        recipe = Recipe.objects.create(user=self.test_user, **self.recipe_data)
        request = self.factory.delete(f'/recipes/{recipe.id}/')
        force_authenticate(request, user=self.test_user)
        view = RecipeViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=recipe.id)

        # Assert that the response status code is 204 (no content)
        self.assertEqual(response.status_code, 204)
        # Assert that the recipe object was deleted from the database
        self.assertEqual(Recipe.objects.count(), 0)

    def test_update_recipe(self):
        recipe = Recipe.objects.create(user=self.test_user, **self.recipe_data)
        put_data = {
            "user": self.test_user.pk,
            "name": "New name",
            "ingredient": "New ingredient",
            "step": "New step",
        }
        request = self.factory.put(f'/recipes/{recipe.pk}/', put_data, format='json')
        force_authenticate(request, user=self.test_user)
        view = RecipeViewSet.as_view({'put': 'update'})
        response = view(request, pk=recipe.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, put_data)

    def test_query_single_recipe(self):
        recipe = Recipe.objects.create(user=self.test_user, **self.recipe_data)
        request = self.factory.get(f'/recipes/{recipe.pk}/', format='json')
        force_authenticate(request, user=self.test_user)
        view = RecipeViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=recipe.pk)

        self.assertEqual(response.status_code, 200)
        expected_data = {"user": self.test_user.pk}
        expected_data.update(self.recipe_data)
        self.assertEqual(response.data, expected_data)

    def test_query_multiple_recipes_by_user_id(self):
        """Query only the list of recipes for the specified person's id"""
        Recipe.objects.create(
            user=self.test_user, name="食谱1", ingredient="...", step="..."
        )
        Recipe.objects.create(
            user=self.test_user, name="食谱2", ingredient="...", step="..."
        )
        Recipe.objects.create(
            user=User.objects.create_user(
                username='test_another', password='test_another'
            ),
            name="其他人的食谱",
            ingredient="...",
            step="...",
        )
        request = self.factory.get(f'/recipes/', format='json')
        force_authenticate(request, user=self.test_user)
        view = RecipeViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        # only 2 recipes belong to self.test_user
        self.assertEqual(len(response.data), 2)


class RecipeModelTest(TestCase):
    def setUp(self) -> None:
        self.recipe_data = {
            "name": "炒饭",
            "ingredient": "米饭，鸡蛋，火腿，青豆",
            "step": "1. 打鸡蛋，加盐搅拌。2. 火腿切小丁，青豆洗净。3. 热锅，倒油，炒鸡蛋。4. 加入米饭，翻炒均匀。5. 加入火腿和青豆，继续翻炒。6. 出锅，盛盘。",
        }
        self.test_user = User.objects.create(username='test', password='test')
        self.recipe = Recipe.objects.create(user=self.test_user, **self.recipe_data)

    def test_recipe_name_is_unique(self):
        with self.assertRaises(Exception):
            # attempt to create a recipe with the same name
            Recipe.objects.create(name="炒饭", ingredient="米饭，鸡蛋，胡萝卜", step="...")

    def test_recipe_name_is_not_empty(self):
        with self.assertRaises(Exception):
            Recipe.objects.create(name="", ingredient="米饭，鸡蛋，胡萝卜", step="...")

    def test_recipe_ingredient_is_not_empty(self):
        with self.assertRaises(Exception):
            # attempt to create a recipe without ingredient
            Recipe.objects.create(name="空白食材", ingredient="", step="...")

    def test_recipe_step_is_not_empty(self):
        with self.assertRaises(Exception):
            # attempt to create a recipe without steps
            Recipe.objects.create(name="无步骤", ingredient="...", step="")

    def test_recipe_user_is_not_empty(self):
        with self.assertRaises(Exception):
            Recipe.objects.create(name="无用户食谱", ingredient="...", step="...")

    def test_recipe_can_be_deleted(self):
        self.recipe.delete()
        self.assertFalse(Recipe.objects.filter(name="炒饭").exists())

    def test_recipe_can_be_updated(self):
        self.recipe.name = "蛋炒饭"
        self.recipe.ingredient = "米饭，鸡蛋"
        self.recipe.step = "1. 打鸡蛋，加盐搅拌。2. 热锅，倒油，炒鸡蛋。3. 加入米饭，翻炒均匀。4. 出锅，盛盘。"
        self.recipe.save()
        # check if the updated recipe is correct
        self.assertEqual(self.recipe.name, "蛋炒饭")
        self.assertEqual(self.recipe.ingredient, "米饭，鸡蛋")
        self.assertEqual(
            self.recipe.step, "1. 打鸡蛋，加盐搅拌。2. 热锅，倒油，炒鸡蛋。3. 加入米饭，翻炒均匀。4. 出锅，盛盘。"
        )

    def test_recipe_can_be_queried(self):
        queried_recipe = Recipe.objects.get(name=self.recipe.name)
        self.assertEqual(queried_recipe.name, self.recipe.name)
