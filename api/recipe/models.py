from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="食谱名")
    ingredient = models.CharField(max_length=200, verbose_name="食材")
    step = models.TextField(max_length=1000, verbose_name="步骤")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="用户",
    )

    def save(self, *args, **kwargs):
        # check if the name field is a empty string
        if self.name == "" or self.ingredient == "" or self.step == "":
            raise ValueError("Name cannot be empty.")

        super().save(*args, **kwargs)
