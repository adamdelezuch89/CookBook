from django import forms
from .models import Recipe, Category, Tag

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'image', 'rating',
            'categories', 'tags', 'prep_time', 'cook_time',
            'idle_time', 'total_time', 'servings', 'ingredients',
            'instructions', 'notes', 'nutrition', 'equipment',
            'video', 'source'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 5}),
            'instructions': forms.Textarea(attrs={'rows': 5}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'nutrition': forms.Textarea(attrs={'rows': 3}),
            'equipment': forms.Textarea(attrs={'rows': 3}),
        } 