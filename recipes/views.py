from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Recipe, Category, ScannedRecipe
from .forms import RecipeForm
from PIL import Image, ImageEnhance
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12  # Number of recipes per page
    
    def get_queryset(self):
        category_id = self.request.GET.get('category')
        queryset = Recipe.objects.all()
        
        if category_id:
            if category_id == 'none':
                queryset = queryset.filter(categories=None)
            else:
                queryset = queryset.filter(categories__id=category_id)
                
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        return context

class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'
    success_url = reverse_lazy('recipes:recipe_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Przepis został dodany pomyślnie!')
        return super().form_valid(form)

class ScanRecipeView(CreateView):
    model = ScannedRecipe
    template_name = 'recipes/scan_recipe.html'
    fields = ['image']
    
    def form_valid(self, form):
        try:
            # Save the scanned recipe
            scanned_recipe = form.save()
            
            # Extract text from image
            scanned_recipe.extract_text()
            
            if not scanned_recipe.scanned_text:
                messages.error(self.request, 'Nie udało się rozpoznać tekstu ze zdjęcia.')
                return redirect('recipes:recipe_create')
            
            # Create recipe from extracted text
            recipe = scanned_recipe.create_recipe()
            
            if recipe:
                messages.success(self.request, 'Przepis został pomyślnie zeskanowany! Możesz go teraz edytować.')
                return redirect('recipes:recipe_update', pk=recipe.pk)
            else:
                messages.warning(
                    self.request, 
                    'Nie udało się rozpoznać przepisu. Spróbuj zrobić wyraźniejsze zdjęcie lub dodaj przepis ręcznie.'
                )
                return redirect('recipes:recipe_create')
                
        except Exception as e:
            logger.error(f"Error scanning recipe: {str(e)}")
            messages.error(
                self.request, 
                'Wystąpił błąd podczas skanowania. Upewnij się, że zdjęcie jest wyraźne i spróbuj ponownie.'
            )
            return redirect('recipes:recipe_create')

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

class RecipeDeleteView(DeleteView):
    model = Recipe
    success_url = reverse_lazy('recipes:recipe_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Przepis został usunięty.')
        return super().delete(request, *args, **kwargs)

class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'
    
    def get_success_url(self):
        return reverse_lazy('recipes:recipe_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Przepis został zaktualizowany!')
        return super().form_valid(form)
