from django.test import TestCase

from .models import Recipe


# Create your tests here.
class RecipeModelTest(TestCase):
    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(
            name="炒饭",
            ingredient="米饭，鸡蛋，火腿，青豆",
            step="1. 打鸡蛋，加盐搅拌。2. 火腿切小丁，青豆洗净。3. 热锅，倒油，炒鸡蛋。4. 加入米饭，翻炒均匀。5. 加入火腿和青豆，继续翻炒。6. 出锅，盛盘。",
        )

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
