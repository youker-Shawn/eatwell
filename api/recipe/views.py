from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from .serializers import RecipeSerializer
from .models import Recipe


# Create your views here.
class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    authentication_classes = [
        SessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        # filter out recipes belonging to this current user
        queryset = Recipe.objects.filter(user=user)
        return queryset
