from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet

router = DefaultRouter()
# list APi viewname: recipe-list.  ref: rest_framework.routers.SimpleRouter.routes
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
