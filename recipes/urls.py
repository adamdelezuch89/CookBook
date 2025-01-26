from django.urls import path
from .views import (
    RecipeListView, RecipeCreateView, ScanRecipeView, 
    RecipeDetailView, RecipeDeleteView, RecipeUpdateView
)

app_name = 'recipes'

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe_list'),
    path('dodaj/', RecipeCreateView.as_view(), name='recipe_create'),
    path('skanuj/', ScanRecipeView.as_view(), name='recipe_scan'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('<int:pk>/usun/', RecipeDeleteView.as_view(), name='recipe_delete'),
    path('<int:pk>/edytuj/', RecipeUpdateView.as_view(), name='recipe_update'),
] 